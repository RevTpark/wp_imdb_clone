from flask import Flask, redirect, render_template, request, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import razorpay
from decouple import config
from utils import fetch_api, fetch_trailers, fetch_youtube_video, get_new_trailers, get_top_movies, get_top_shows, login_required


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = config("SQLALCHEMY_DATABASE_URI")
app.config["SECRET_KEY"] = config("SECRET_KEY")
db = SQLAlchemy(app)

from models import User, Movie, Order, Cart, init_db_command, seed_data_command
from forms import LoginForm, RegisterUserForm, UpdateUserForm

app.cli.add_command(init_db_command)
app.cli.add_command(seed_data_command)

@app.route("/")
def home():
    if session.get("user_id", False):
        user = User.query.filter_by(id=session['user_id']).first()
        if user.is_admin:
            orders = Order.query.all()
            client = razorpay.Client(auth=(config("RAZORPAY_KEY_ID"), config("RAZORPAY_KEY_SECRET")))
            data = []
            total_profit = 0
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
                total_profit += resp["amount"]/100
            return render_template("admin_dashboard.html", data=data, total=total_profit)

    top_movies = get_top_movies()
    top_series = get_top_shows()
    new_trailers = get_new_trailers()
    data = {
        "movies": top_movies,
        "series": top_series,
        "trailers": new_trailers
    }
    return render_template("home.html", data=data)


@app.route("/search", methods=["GET", "POST"])
def search_movies():
    data = []
    if request.method == "POST":
        title = request.form.get("search")
        if not title:
            flash("Please enter a movie title.", "info")
            return redirect(url_for("home"))
        data = fetch_api("s", title)

        if not data.get("Search"):
            flash("No movies with such title exists.", "info")
            return redirect(url_for("home"))
        data = data["Search"]
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


@app.route("/profile")
@login_required
def profile():
    user = User.query.filter_by(id=session["user_id"]).first()
    return render_template("profile.html", data=user)

@app.route("/profile/update", methods=["GET", "POST"])
@login_required
def profile_update():
    user = User.query.filter_by(id=session["user_id"]).first()
    form = UpdateUserForm(obj=user)
    if form.validate_on_submit():
        form.populate_obj(user)
        db.session.commit()
        flash("Details updated successfully!", "success")
        return redirect(url_for('profile'))
    return render_template("updateProfile.html", form=form)


@app.route("/delete")
@login_required
def delete_account():
    user = User.query.filter_by(id=session["user_id"]).first()
    db.session.delete(user)
    db.session.commit()
    flash("Account deleted successfully!", "success")
    return redirect(url_for("home"))


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


@app.route("/cart/add/<item_id>/<product_name>")
@login_required
def add_to_cart(item_id, product_name):
    user = User.query.filter_by(id=session["user_id"]).first()
    if Cart.query.filter(Cart.product_id==item_id, Cart.user_id==user.id).first():
        flash("Product already exists in cart.", "info")
        return redirect(url_for("cart"))
    
    if Order.query.filter(Order.movie_id==item_id, Order.user_id==user.id).first():
        flash("You have already brought this movie.", "info")
        return redirect(url_for("watchlist"))
    
    new_cart_item = Cart(
        user_id=user.id,
        product_id=item_id,
        amount=50000,
        product_title=product_name
    )
    db.session.add(new_cart_item)
    db.session.commit()
    flash(f"{product_name} added to cart successfully!", "success")
    return redirect(url_for("cart"))


@app.route("/cart/delete/<product_id>")
@login_required
def remove_from_cart(product_id):
    product = Cart.query.filter(Cart.product_id==product_id, Cart.user_id==session['user_id']).first()
    db.session.delete(product)
    db.session.commit()
    flash("Removed item from cart successfully!", "success")
    return redirect(url_for("cart"))


@app.route("/cart")
@login_required
def cart():
    user = User.query.filter_by(id=session["user_id"]).first()
    cart_list = Cart.query.filter_by(user_id=user.id).all()
    data = []
    total = 0
    for item in cart_list:
        details = fetch_api("i", item.product_id)
        data.append({
            "amount": item.amount/100,
            "movie": details
        })
        total += data[-1]["amount"]
    
    return render_template("cart.html", data=data, total=total)


@app.route("/checkout")
@login_required
def checkout():
    cart_list = Cart.query.filter_by(user_id=session['user_id']).all()
    total = 0
    for item in cart_list:
        total += item.amount/100
    
    client = razorpay.Client(auth=(config("RAZORPAY_KEY_ID"), config("RAZORPAY_KEY_SECRET")))
    order_data = {
        "amount": total*100,
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

    return render_template("checkout.html", config=config, payment=payment, details=user_details, cart=cart_list)


@app.route("/pay/verify/cart", methods=["GET", "POST"])
@login_required
def pay_verify_cart():
    client = razorpay.Client(auth=(config("RAZORPAY_KEY_ID"), config("RAZORPAY_KEY_SECRET")))

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
        cart_list = Cart.query.filter_by(user_id=session['user_id']).all()
        for item in cart_list:
            new_movie = Movie(
                user_id=session["user_id"],
                movie_title=item.product_title,
                movie_id=item.product_id
            )
            db.session.add(new_movie)
            db.session.commit()

            new_order = Order(
                user_id=session["user_id"],
                movie_id=item.product_id,
                order_id=order_id,
                payment_id=payment_id,
                signature=signature
            )
            db.session.add(new_order)
            db.session.commit()
        
        for item in cart_list:
            db.session.delete(item)
            db.session.commit()
        
        flash("Product Purchase Successful!", "success")
        return redirect(url_for("watchlist"))
    flash("Payment could not be verified.", "success")
    return redirect(url_for("cart"))


@app.route("/buy/<movie_id>", methods=["GET", "POST"])
@login_required
def buy_movie(movie_id):
    user = User.query.filter_by(id=session["user_id"]).first()
    
    if Order.query.filter(Order.movie_id==movie_id, Order.user_id==user.id).first():
        flash("You have already brought this movie.", "info")
        return redirect(url_for("watchlist"))
    
    data = fetch_api("i", movie_id)
    client = razorpay.Client(auth=(config("RAZORPAY_KEY_ID"), config("RAZORPAY_KEY_SECRET")))
    order_data = {
        "amount": 50000,
        "currency": "INR",
        "receipt": "#24"
    }
    payment = client.order.create(data=order_data)
    
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
    flash("Payment could not be verified.", "error")
    return redirect(url_for("home"))


@app.route("/pay/failure", methods=["GET", "POST"])
@login_required
def pay_failure():
    flash("There was some error in payment gateway.", "error")
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)