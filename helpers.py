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

# Flask routes with @upload_required require users to upload today before accessing. Redirects to /upload
def upload_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("uploaded") is False:
            flash("You'll need to upload the snapshot for today!")
            return redirect("/upload")
        return f(*args, **kwargs)
    return decorated_function

# Flask routes with @new_upload_required require users to not have uploaded today in order to access. Redirects to /index
def new_upload_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("uploaded") is True:
            flash("You've already uploaded a snapshot for today!")
            return redirect("/")
        return f(*args, **kwargs)
    return decorated_function



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

