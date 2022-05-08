from flask import Flask, redirect, render_template, request, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import razorpay
from decouple import config
from utils import fetch_api, fetch_youtube_video, get_top_movies, login_required


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = config("SQLALCHEMY_DATABASE_URI")
app.config["SECRET_KEY"] = config("SECRET_KEY")
db = SQLAlchemy(app)

from models import User, Movie, Order
from forms import LoginForm, RegisterUserForm

@app.route("/")
def home():
    if session.get("user_id", False):
        user = User.query.filter_by(id=session['user_id']).first()
        if user.is_admin:
            orders = Order.query.all()
            client = razorpay.Client(auth=(config("RAZORPAY_KEY_ID"), config("RAZORPAY_KEY_SECRET")))
            data = []
            for order in orders:
                resp = client.payment.fetch(order.payment_id)
                movie_details = Movie.query.filter_by(movie_id=order.movie_id).first()
                data.append({
                    "payment_id": order.payment_id,
                    "amount": resp["amount"]/100,
                    "movie_title": movie_details.movie_title,
                    "email": resp["email"],
                    "phone_number": resp["contact"],
                    "method": resp["method"].capitalize()
                })
            return render_template("admin_dashboard.html", data=data)

    top_movies = get_top_movies()
    return render_template("home.html", data=top_movies)

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
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            session["user_id"] = user.id
            flash("Logged In Successfully!", "success")
            return redirect(url_for("home"))
        flash("Incorrect credentials provided.", "error")
    return render_template("signIn.html", form=form)


@app.route("/logout")
@login_required
def sign_out():
    if session.get("user_id"):
        session.pop("user_id")
        flash("Logged Out Successfully!", "success")
    return redirect(url_for("home"))


@app.route("/register", methods=["GET", "POST"])
def sign_up():
    form = RegisterUserForm()
    if form.validate_on_submit():
        new_user = User(
            name=form.name.data,
            email=form.email.data,
            address=form.address.data,
            city=form.city.data,
            state=form.state.data,
            pin_code=form.pin_code.data,
            phone_number=form.phone_number.data,
        )
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash("Registered Successfully!", "success")
        return redirect(url_for("home"))
    return render_template("signUp.html", form=form)


@app.route("/movies/<movie_id>")
def movie_details(movie_id):
    data = fetch_api("i", movie_id)
    data["Genre"] = data["Genre"].split(",")
    data["Actors"] = data["Actors"].split(",")
    data["Type"] = data["Type"].capitalize()

    temp_data = fetch_api("i", movie_id, "full")
    data["Plot_Full"] = temp_data["Plot"]

    data['videoId'] = fetch_youtube_video(data['Title']+"trailer")
    return render_template("movieDetails.html", movie=data)


@app.route("/mylist")
@login_required
def watchlist():
    movies = Movie.query.filter_by(user_id=session['user_id']).all()
    return render_template("watchlist.html", movies=movies, enumerate=enumerate, len=len)


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
        flash("Product Purchase Successful!", "success")
        return redirect(url_for("watchlist"))
    flash("Payment could not be verified", "error")
    return redirect(url_for("home"))


@app.route("/pay/failure")
@login_required
def pay_failure():
    flash("There was some error in payment gateway.", "error")
    return render_template("home.html")


if __name__ == "__main__":
    app.run(debug=True)