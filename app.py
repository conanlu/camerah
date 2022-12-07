import os
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required, password_check, upload_required, new_upload_required
import datetime
import cv2
import firebase_admin
from firebase_admin import credentials, firestore
import sys
import random

# Configure application
app = Flask(__name__)


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///camerah.db")
# Create variable specifying prefix for where all photos are stored
PREFIX = "static/photos/"



# CONSTANTS: developers can change as they see fit

IMG_DIMENSION = 1080 # Crops or expands each photos to fit 1080 x 1080 frame.
VIDEO_FPS = 3
LOCATION = "Placeholder" # Location of the day
NUM_LOCATIONS = 3 # Number of normal locations in database. Currently 3


# UTILITY FUNCTIONS 

#Cropping a photo
def crop(dst):
    frame = cv2.imread(dst)
    os.remove(dst)
    height, width, layers = frame.shape
    if height > width:
        frame = frame[:width, :width]
    else:
        frame = frame[:height, :height]
    frame = cv2.resize(frame, (IMG_DIMENSION, IMG_DIMENSION), cv2.INTER_AREA)
    cv2.imwrite(dst, frame)

# Getting the date today in YYYY-MM-DD format
def getToday():
    x = datetime.datetime.now(datetime.timezone.utc)
    formatted = x.strftime("%Y")+"-"+x.strftime("%m")+"-"+x.strftime("%d")
    return formatted


# Creates a video of all images in a folder with 
def video(image_folder):
    video_name = "static/video.avi"
    images = [img for img in os.listdir(image_folder) if
              img.endswith(".png") or img.endswith(".jpg") or img.endswith(".PNG") or img.endswith(".JPG") or img.endswith(".JPEG") or img.endswith(".jpeg")]
    frame = cv2.imread(os.path.join(image_folder, images[0]))
    frame = cv2.flip(frame, 1)
    height, width, layers = frame.shape
    ratio = 1.0 * height / width
    video = cv2.VideoWriter(video_name, 0, VIDEO_FPS, (width, height))

    for image in images:
        tmp = cv2.imread(os.path.join(image_folder, image))
        tmp = cv2.flip(tmp, 1)
        video.write(tmp)

    cv2.destroyAllWindows()
    video.release()

# Checks if user uploaded today. This value is used for @upload_required
def checkUploaded():
    x = getToday()
    dates = db.execute("SELECT date FROM photos WHERE user_id = ?", session["user_id"])
    session["uploaded"] = False
    for d in dates:
        if x in d["date"]:
            session["uploaded"] = True
            return True
    return False


# Connecting to Firebase

cred = credentials.Certificate("serviceAccountKey.json") # Replace this with your path to the Firestore key
firebase_admin.initialize_app(cred)


fdb = firestore.client()  # this connects to our Firestore database
collection = fdb.collection('locations')  # opens 'places' collection


# Initializing location for the day
# If there is a "special" location for a particular day, then loads that (e.g. CS50 FAIR, 2022-12-07)
# Otherwise, loops through normal locations
today = int(datetime.datetime.now(datetime.timezone.utc).strftime("%d")) * 1000 + int(datetime.datetime.now(datetime.timezone.utc).strftime("%d"))
doc = collection.document(getToday()).get()
if doc.exists:
    LOCATION = doc.to_dict()['name']
else:
    doc = collection.document(str(today % NUM_LOCATIONS + 1)).get()
    LOCATION = doc.to_dict()['name']



@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
@login_required
# Require user to upload an image before viewing feed for the day
@upload_required
def index():
    checkUploaded()
    if request.method == "GET": # If user is loading home page
        # get username
        username = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])[0]["username"]
        # get current day
        today = getToday()
        # get all pictures taken today
        pics =  db.execute("SELECT * FROM photos WHERE date LIKE ? ORDER BY upvotes DESC", today+"%")
        # get all pictures liked by the user
        liked = db.execute("SELECT name FROM photos WHERE id IN (SELECT photo_id FROM likes WHERE user_id = ?)", session["user_id"])        
        # if there are pictures posted today, add to dictionary that links uploaded photo names (keys) and upvotes (values)
        if len(pics) != 0:
            imgs = dict()
            for pic in pics:
                imgs[pic.get("name")] = pic.get("upvotes")
            likes = list()
            for like in liked:
                likes.append(like.get("name")) # create list of photos posted today and liked by user
            # send username, images posted today, prefix for all photos, and list of liked images to index.html
            return render_template("index.html", username=username, imgs=imgs, prefix = PREFIX, likes=likes, location=LOCATION)
        # if no photos have been posted today, just send username to index.html
        return render_template("index.html", username=username, location=LOCATION)
    else: # if the user clicked a "like" button
        # get name of photo user liked
        name = request.form.get("upvote")
        # get id of photo user liked
        photoid = db.execute("SELECT id FROM photos WHERE name = ?", name)[0]["id"]
        # update photos and likes databases with user's like
        db.execute("UPDATE photos SET upvotes = upvotes + 1 WHERE name = ?", name)
        db.execute("INSERT INTO likes (user_id, photo_id) VALUES(?, ?)", session["user_id"], photoid)
        # load home page
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
        if not username or not password or not confirmation:
            return apology("must fill out all fields")

        if password != confirmation:
            return apology("passwords must match")

        username_taken = db.execute("SELECT * from USERS where username = ?", username)
        if username_taken:
            return apology("username taken")

        # our additional requirement for extra security: password must have 8 characters, one of which must be number
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
    if request.method == "GET": # if user clicked "upload" button
        return render_template("upload.html", location=LOCATION)
    else: # if user is trying to upload file
       img = request.files.getlist("file")[0] # get image from the upload html
       if not img:
        return apology("must upload photo")
       # Code from https://bobbyhadz.com/blog/python-replace-spaces-with-underscores
       # spaces in file names cause problems, so replace all spaces with underscores before progressing
       imgname = img.filename.replace(' ', '_')
       # save image in static/photos
       img.save(os.path.join(PREFIX, imgname))
       # crop image to look uniform on feed
       crop(os.path.join(PREFIX, imgname))
       # insert photos into database
       db.execute("INSERT INTO photos (name, user_id, upvotes) VALUES(?, ?, ?)", imgname, session["user_id"], 0)
       checkUploaded()
       return redirect("/")

@app.route("/collage", methods=["GET"])
def collage():
    """Access collage"""
    if request.method == "GET":

        # create a new "video.avi" file based on photos
        video("static/photos")

        # load photos
        pics =  db.execute("SELECT name FROM photos ORDER BY date DESC")
        if len(pics) == 0:
            return render_template("nocollage.html")
        imgs = list()
        for pic in pics:
            imgs.append(pic.get("name"))
        return render_template("collage.html", imgs=imgs, prefix=PREFIX)
