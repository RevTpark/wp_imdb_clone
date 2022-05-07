import requests
from flask import session, redirect, url_for, flash
from functools import wraps

def fetch_api(param, titleOrId, plot="short"):
    url = (f"http://www.omdbapi.com/?apikey=ca4430d&{param}={titleOrId}&plot={plot}")
    response = requests.get(url)
    data = response.json()
    return data

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if not session.get("user_id", False):
            flash("User Login required for access.", "error")
            return redirect(url_for("home"))
        else:
            return f(*args, **kwargs)
    return wrap