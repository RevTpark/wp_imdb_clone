from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/login", methods=["GET", "POST"])
def sign_in():
    return render_template("signIn.html")


@app.route("/register", methods=["GET", "POST"])
def sign_up():
    return render_template("signUp.html")


@app.route("/movies/details")
def movie_details():
    return render_template("movieDetails.html")


@app.route("/watchlist")
def watchlist():
    return render_template("watchlist.html")


if __name__ == "__main__":
    app.run(debug=True)