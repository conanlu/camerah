import os
import requests
import urllib.parse

from flask import redirect, render_template, request, session, flash
from functools import wraps


def apology(message, code=400):
    """Render message as an apology to user."""

    return render_template("apology.html", top=code, bottom=message), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            flash("You'll need to log in!")
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def upload_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("uploaded") is False:
            flash("You'll need to upload the snapshot for today!")
            return redirect("/upload")
        return f(*args, **kwargs)
    return decorated_function


def new_upload_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("uploaded") is True:
            flash("You've already uploaded a snapshot for today!")
            return redirect("/")
        return f(*args, **kwargs)
    return decorated_function


def lookup(symbol):
    """Look up quote for symbol."""

    # Contact API
    try:
        api_key = os.environ.get("API_KEY")
        url = f"https://cloud.iexapis.com/stable/stock/{urllib.parse.quote_plus(symbol)}/quote?token={api_key}"
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        quote = response.json()
        return {
            "name": quote["companyName"],
            "price": float(quote["latestPrice"]),
            "symbol": quote["symbol"]
        }
    except (KeyError, TypeError, ValueError):
        return None


def usd(value):
    """Format value as USD."""
    # this returns value as usd
    return f"${value:,.2f}"


def password_check(str):
    # check if password length is less than 8
    if len(str) < 8:
        return False
    # check if any characters in string are numbers
    for c in str:
        # iterating through string
        if c.isdigit():
            # returning true if found number
            return True
    # if not found, return FAIL
    return False

