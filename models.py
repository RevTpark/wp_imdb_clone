from app import db
from bcrypt import checkpw, hashpw, gensalt
import click
from flask.cli import with_appcontext

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)
    city = db.Column(db.String(255), nullable=False)
    state = db.Column(db.String, nullable=False)
    pin_code = db.Column(db.Integer, nullable=False)
    phone_number = db.Column(db.Integer, nullable=False)

    owned_movies = db.relationship("Movie", cascade="all, delete", backref="User", lazy=True)
    payments_done = db.relationship("Order", cascade="all, delete", backref="User", lazy=True)

    def set_password(self, password):
        self.password = hashpw(password.encode('utf-8'), gensalt()).decode('ascii')

    def check_password(self, password):
        return checkpw(password.encode('utf-8'), self.password.encode('utf-8'))


class Movie(db.Model):
    __tablename__ = "movies"
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, primary_key=True)
    movie_title = db.Column(db.String, nullable=False)
    movie_id = db.Column(db.String, nullable=False, primary_key=True)

    payment_info = db.relationship("Order", cascade="all, delete", backref="Movie", lazy=True)


class Order(db.Model):
    __tablename__ = "orders"
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, primary_key=True)
    movie_id = db.Column(db.String, db.ForeignKey("movies.movie_id"), nullable=False, primary_key=True)
    order_id = db.Column(db.String, nullable=False, primary_key=True)
    payment_id = db.Column(db.String, nullable=False, unique=True)
    signature = db.Column(db.String, nullable=False)


@click.command('init-db')
@with_appcontext
def init_db_command():
    db.create_all()   
    click.echo('Initialized the database.')

@click.command('seed-data')
@with_appcontext
def seed_data_command():
    admin = User(
        name="Admin",
        email="admin@gmail.com",
        address="221b Baker Street",
        city="New York",
        state="Texas",
        pin_code="520861",
        phone_number="9876543210",
        is_admin=True
    )
    admin.set_password("admin")
    db.session.add(admin)
    db.session.commit()

    consumer = User(
        name="Marc Spector",
        email="marc.spector@gmail.com",
        address="221b Baker Street",
        city="New York",
        state="Texas",
        pin_code="520861",
        phone_number="9876543210",
    )
    consumer.set_password("password")
    db.session.add(consumer)
    db.session.commit()

    click.echo('Data Seeeded.')