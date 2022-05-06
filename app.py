from flask import Flask, render_template, request
import requests

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("home.html")

@app.route("/search", methods=["GET", "POST"])
def search_movies():
    data = []
    if request.method == "POST":
        title = request.form.get("search")
        url = (f"http://www.omdbapi.com/?apikey=ca4430d&s={title}")
        response = requests.get(url)
        data = response.json()["Search"]
        for cnt, movie in enumerate(data):
            url = (f"http://www.omdbapi.com/?apikey=ca4430d&i={movie['imdbID']}")
            response = requests.get(url)
            details = response.json()
            data[cnt]["Type"] = data[cnt]["Type"].capitalize()
            data[cnt]["Plot"] = details["Plot"]
            data[cnt]["Genre"] = details["Genre"]
    return render_template('displayMovies.html', movies=data)


@app.route("/login", methods=["GET", "POST"])
def sign_in():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
    return render_template("signIn.html")


@app.route("/register", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        address = request.form.get("address")
        city = request.form.get("city")
        state = request.form.get("state")
        pin_code = request.form.get("pin-code")
        phone_number = request.form.get("number")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
    return render_template("signUp.html")


@app.route("/movies/<movie_id>")
def movie_details(movie_id):
    url = (f"http://www.omdbapi.com/?apikey=ca4430d&i={movie_id}")
    response = requests.get(url)
    data = response.json()
    data["Genre"] = data["Genre"].split(",")
    data["Actors"] = data["Actors"].split(",")

    url = (f"http://www.omdbapi.com/?apikey=ca4430d&i={movie_id}&plot=full")
    response = requests.get(url)
    temp_data = response.json()
    data["Plot_Full"] = temp_data["Plot"]
    return render_template("movieDetails.html", movie=data)


@app.route("/watchlist")
def watchlist():
    return render_template("watchlist.html")


if __name__ == "__main__":
    app.run(debug=True)