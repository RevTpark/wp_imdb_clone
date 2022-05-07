from flask import Flask, redirect, render_template, request, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import razorpay
from decouple import config
from utils import fetch_api, login_required

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = config("SQLALCHEMY_DATABASE_URI")
app.config["SECRET_KEY"] = config("SECRET_KEY")
db = SQLAlchemy(app)

from models import User, Movie, Order

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/search", methods=["GET", "POST"])
def search_movies():
    data = []
    if request.method == "POST":
        title = request.form.get("search")
        data = fetch_api("s", title)["Search"]
        for cnt, movie in enumerate(data):
            details = fetch_api("i", movie['imdbID'])
            data[cnt]["Type"] = data[cnt]["Type"].capitalize()
            data[cnt]["Plot"] = details["Plot"]
            data[cnt]["Genre"] = details["Genre"]
    return render_template('displayMovies.html', movies=data)


@app.route("/login", methods=["GET", "POST"])
def sign_in():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session["user_id"] = user.id
            
            return redirect(url_for("home"))
    return render_template("signIn.html")


@app.route("/logout")
@login_required
def sign_out():
    if session.get("user_id"):
        session.pop("user_id")
    return redirect(url_for("home"))


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

        new_user = User(
            name=name,
            email=email,
            address=address,
            city=city,
            state=state,
            pin_code=pin_code,
            phone_number=phone_number,
        )
        new_user.set_password(password1)
        db.session.add(new_user)
        db.session.commit()

    return render_template("signUp.html")


@app.route("/movies/<movie_id>")
def movie_details(movie_id):
    data = fetch_api("i", movie_id)
    data["Genre"] = data["Genre"].split(",")
    data["Actors"] = data["Actors"].split(",")
    data["Type"] = data["Type"].capitalize()

    temp_data = fetch_api("i", movie_id, "full")
    data["Plot_Full"] = temp_data["Plot"]
    return render_template("movieDetails.html", movie=data)


@app.route("/mylist")
@login_required
def watchlist():
    movies = Movie.query.filter_by(user_id=session['user_id']).all()

    return render_template("watchlist.html", movies=movies, enumerate=enumerate)


@app.route("/buy/<movie_id>", methods=["GET", "POST"])
@login_required
def buy_movie(movie_id):
    data = fetch_api("i", movie_id)
    client = razorpay.Client(auth=(config("RAZORPAY_KEY_ID"), config("RAZORPAY_KEY_SECRET")))
    order_data = {
        "amount": 50000,
        "currency": "INR",
        "receipt": "#24"
    }
    payment = client.order.create(data=order_data)
    user = User.query.filter_by(id=session["user_id"]).first()
    user_details = {
        "name": user.name,
        "email": user.email,
        "ph_nm": user.phone_number,
        "payment": payment
    }
    return render_template("buyMovie.html", movie=data, details=user_details, config=config)


@app.route("/pay/verify", methods=["GET", "POST"])
@login_required
def pay_verify():
    client = razorpay.Client(auth=(config("RAZORPAY_KEY_ID"), config("RAZORPAY_KEY_SECRET")))

    movie_id = request.form.get("movie_id")
    payment_id = request.form.get("payment_id")
    order_id = request.form.get("order_id")
    signature = request.form.get("signature")
    params_dict = {
        'razorpay_order_id': order_id,
        'razorpay_payment_id': payment_id,
        'razorpay_signature': signature
    }
    res = client.utility.verify_payment_signature(params_dict)
    if res:
        movie_name = fetch_api("i", movie_id)["Title"]
        new_movie = Movie(
            user_id=session["user_id"],
            movie_title=movie_name,
            movie_id=movie_id
        )
        db.session.add(new_movie)
        db.session.commit()

        new_order = Order(
            user_id=session["user_id"],
            movie_id=movie_id,
            order_id=order_id,
            payment_id=payment_id,
            signature=signature
        )
        db.session.add(new_order)
        db.session.commit()
        return redirect(url_for("watchlist"))
    
    return redirect(url_for("home"))


@app.route("/pay/failure")
@login_required
def pay_failure():
    return render_template("home.html")


if __name__ == "__main__":
    app.run(debug=True)