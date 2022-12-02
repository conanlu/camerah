# personal touches: requiring at least 8 characters and 1 number for password to be valid, also displaying user's username above portfolio
import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd, password_check
from datetime import time

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

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


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    stocks = {}
    # displays username
    username = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])[0]["username"]
    user_purchases = db.execute("SELECT * FROM purchases WHERE user_id = ?", session["user_id"])
    # creating a dictionary tracking cumulative stocks and num. shares user has currently
    for row in user_purchases:
        if row["symbol"] in stocks:
            stocks[row["symbol"]] += int(row["shares"])
        else:
            stocks[row["symbol"]] = int(row["shares"])

    # creating custom table for display
    table = []
    # cum_total: total money in stock right now
    cum_total = 0
    for symbol, shares in stocks.items():
        new = []
        l = lookup(symbol)
        # stock symbol, name, price, and total
        new.append(l["symbol"])
        new.append(l["name"])
        new.append(usd(l["price"]))
        new.append(shares)
        new.append(usd(shares*l["price"]))
        cum_total += shares*l["price"]
        if shares != 0:
            table.append(new)

    # displaying user balance
    balance = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])[0]["cash"]
    return render_template("index.html", table=table, total=usd(cum_total), cash=usd(balance), username=username, cash_yass=False)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    if request.method == "POST":

        # pre-processing symbol/shares so that incorrect inputs get filtered out
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")
        if not shares.isdigit():
            return apology("number of shares should be an integer")
        shares = int(shares)

        l = lookup(symbol)
        if l is None:
            return apology("input a valid symbol PLEEK")
        if shares <= 0:
            return apology("number of shares should be positive")

        # money transaction (or lack thereof)
        balance = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])[0]["cash"]
        cost = shares * l["price"]
        if cost > balance:
            return apology("insufficient funds")
        balance = balance - cost

        # updating database
        db.execute("UPDATE users SET cash = ? WHERE id = ?", balance, session["user_id"])
        db.execute("INSERT INTO purchases (user_id, symbol, shares) VALUES(?,?,?)", session["user_id"], l["symbol"], shares)
        return redirect("/")
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    # transaction history - only some columns from purchases needed
    transactions = db.execute("SELECT symbol,shares,date FROM purchases WHERE user_id = ? ", session["user_id"])
    return render_template("history.html", table=transactions)


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


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    if request.method == "POST":
        symbol = request.form.get("symbol")
        l = lookup(symbol)
        if l is None:
            return apology("input a valid symbol PLEEK")
        # show price of stock
        return render_template("quoted.html", symbol=l["symbol"], price=usd(l["price"]), name=l["name"])
    else:
        # show form if not post
        return render_template("quote.html")


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


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    # sets up inventory of user's current stocks
    stocks = {}
    user_purchases = db.execute("SELECT * FROM purchases WHERE user_id = ?", session["user_id"])
    for row in user_purchases:
        if row["symbol"] in stocks:
            stocks[row["symbol"]] += int(row["shares"])
        else:
            stocks[row["symbol"]] = int(row["shares"])

    symbols = []

    for symbol in stocks:
        if stocks[symbol] != 0:
            symbols.append(symbol)

    if request.method == "POST":
        sym = request.form.get("symbol")

        shares = request.form.get("shares")
        if not shares.isdigit():
            return apology("number of shares should be an integer")
        shares = -1*int(shares)
        if (shares >= 0):
            return apology("shares must be positive")

        # checks if number of stocks reasonable
        print("stocks")
        print(stocks[sym])
        if -1 * shares > stocks[sym]:
            return apology("you're selling more stocks than you have")

        l = lookup(sym)

        # makes changes to database and user balance
        balance = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])[0]["cash"]
        change = shares * l["price"]
        db.execute("UPDATE users SET cash = ? WHERE id = ?", balance - change, session["user_id"])
        db.execute("INSERT INTO purchases (user_id, symbol, shares) VALUES(?,?,?)", session["user_id"], l["symbol"], shares)
        return redirect("/")

    else:
        # if not post: shows form
        return render_template("sell.html", symbols=symbols)


@app.route("/upload", methods=["GET", "POST"])
def upload():
    """Upload photo"""
    if request.method == "GET":
        return render_template("upload.html")


@app.route("/collage", methods=["GET"])
def collage():
    """Access collage"""
    if request.method == "GET":
        return render_template("collage.html")
