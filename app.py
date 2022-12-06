# personal touches: requiring at least 8 characters and 1 number for password to be valid, also displaying user's username above portfolio
import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd, password_check, upload_required, new_upload_required
import datetime
import cv2

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)



# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///camerah.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
@login_required
@upload_required
def index():
    checkUploaded()
    if request.method == "GET": 
        username = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])[0]["username"]
        today = getToday()
        pics =  db.execute("SELECT * FROM photos WHERE date LIKE ? ORDER BY upvotes DESC", today+"%")
        liked = db.execute("SELECT name FROM photos WHERE id IN (SELECT photo_id FROM likes WHERE user_id = ?)", session["user_id"])        
        if len(pics) != 0:
            imgs = dict()
            for pic in pics:
                imgs[pic.get("name")] = pic.get("upvotes")
            likes = list()
            for like in liked:
                likes.append(like.get("name"))
            return render_template("index.html", username=username, imgs=imgs, prefix = "static/photos/", likes=likes)
        return render_template("index.html", username=username)
    else:
        name = request.form.get("upvote")
        photoid = db.execute("SELECT id FROM photos WHERE name = ?", name)[0]["id"]
        db.execute("UPDATE photos SET upvotes = upvotes + 1 WHERE name = ?", name)
        db.execute("INSERT INTO likes (user_id, photo_id) VALUES(?, ?)", session["user_id"], photoid)
        return redirect("/")
        

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        checkUploaded()
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        # preprocessing username/password input to make sure unique and satisfies requirements
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        if password != confirmation:
            return apology("passwords must match")

        username_taken = db.execute("SELECT * from USERS where username = ?", username)
        if username_taken:
            return apology("username taken")

        if not password_check(password):
            return apology("passwords must have at least 8 characters, at least one of which must be a number")

        # enters user into database
        db.execute("INSERT INTO users (username, hash) VALUES(?,?)", username, generate_password_hash(password))
        return redirect("/")
    else:
        return render_template("register.html")

@app.route("/upload", methods=["GET", "POST"])
@login_required
@new_upload_required
def upload():
    """Upload photo"""
    if request.method == "GET":
        return render_template("upload.html")
    else:
       img = request.files.getlist("file")[0]
       # Code from https://bobbyhadz.com/blog/python-replace-spaces-with-underscores
       imgname = img.filename.replace(' ', '_')
       img.save(os.path.join("./static/photos", imgname))
       crop(os.path.join("./static/photos", imgname))
       db.execute("INSERT INTO photos (name, user_id, upvotes) VALUES(?, ?, ?)", imgname, session["user_id"], 0)
       checkUploaded()
       return redirect("/")

@app.route("/collage", methods=["GET"])
def collage():
    """Access collage"""
    if request.method == "GET":
        pics =  db.execute("SELECT name FROM photos ORDER BY upvotes DESC LIMIT 9")
        if len(pics) < 9:
            return render_template("nocollage.html")
        imgs = list()
        for pic in pics:
            imgs.append(pic.get("name"))
        return render_template("collage.html", imgs=imgs, prefix = "static/photos/")

def checkUploaded():
    x = getToday()
    dates = db.execute("SELECT date FROM photos WHERE user_id = ?", session["user_id"])
    session["uploaded"] = False
    for d in dates:
        if x in d["date"]:
            session["uploaded"] = True
            return True
    return False

def getToday():
    x = datetime.datetime.now(datetime.timezone.utc)
    formatted = x.strftime("%Y")+"-"+x.strftime("%m")+"-"+x.strftime("%d")
    return formatted

def crop(dst):
    frame = cv2.imread(dst)
    os.remove(dst)
    height, width, layers = frame.shape
    if height > width:
        frame = frame[:width, :width]
    else:
        frame = frame[:height, :height]
    cv2.imwrite(dst, frame)