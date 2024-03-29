from decouple import config
import requests
from flask import session, redirect, url_for, flash
from functools import wraps
import os
import googleapiclient.discovery
import googleapiclient.errors
from constants import top_movies, top_series, new_trailers

def fetch_api(param, titleOrId, plot="short"):
    url = (f"http://www.omdbapi.com/?apikey=ca4430d&{param}={titleOrId}&plot={plot}")
    response = requests.get(url)
    data = response.json()
    return data

def get_top_movies():
    return top_movies['items']

def get_top_shows():
    return top_series['items']

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if not session.get("user_id", False):
            flash("User Login required for access.", "error")
            return redirect(url_for("home"))
        else:
            return f(*args, **kwargs)
    return wrap


def fetch_youtube_video(query):
    scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"

    # Get credentials and create an API client
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey=config("API_KEY"))

    request = youtube.search().list(
        part="snippet",
        q=query,
        type="video",
        maxResults=5
    )
    response = request.execute()

    if len(response['items']) > 0:
        return response['items'][0]['id']['videoId']
    else:
        return "xjDjIWPwcPU"

def fetch_trailers(query):
    scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"

    # Get credentials and create an API client
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey=config("API_KEY"))

    request = youtube.search().list(
        part="snippet",
        q="new trailers",
        regionCode="US",
        relevanceLanguage="en",
        maxResults=5
    )
    response = request.execute()
    return response['items']

def get_new_trailers():
    return new_trailers