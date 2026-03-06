from flask import Flask, render_template, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user
import os

app = Flask(__name__)
app.secret_key = "secret123"

DATABASE_URL = os.environ.get("DATABASE_URL")

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)


# --------------------
# DATABASE MODELS
# --------------------

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))


class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    nationality = db.Column(db.String(50))
    team = db.Column(db.String(100))
    strike_rate = db.Column(db.Float)
    performance = db.Column(db.Float)
    current_bid = db.Column(db.Integer)


class Bid(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    player_id = db.Column(db.Integer)
    bid_amount = db.Column(db.Integer)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# --------------------
# ROUTES
# --------------------

@app.route("/")
def home():

    nationality = request.args.get("nation")

    if nationality:
        players = Player.query.filter_by(nationality=nationality).all()
    else:
        players = Player.query.all()

    return render_template("index.html", players=players)


@app.route("/register", methods=["POST"])
def register():

    username = request.form["username"]
    password = request.form["password"]

    user = User(username=username, password=password)

    db.session.add(user)
    db.session.commit()

    return redirect("/")


@app.route("/login", methods=["POST"])
def login():

    username = request.form["username"]
    password = request.form["password"]

    user = User.query.filter_by(username=username, password=password).first()

    if user:
        login_user(user)

    return redirect("/")


@app.route("/bid", methods=["POST"])
@login_required
def bid():

    player_id = request.form["player_id"]
    bid_amount = int(request.form["bid_amount"])

    player = Player.query.get(player_id)

    if bid_amount > player.current_bid:

        player.current_bid = bid_amount

        new_bid = Bid(
            user_id=current_user.id,
            player_id=player_id,
            bid_amount=bid_amount
        )

        db.session.add(new_bid)
        db.session.commit()

        return redirect("/")

    return "Bid must be higher than current bid"


# --------------------
# CREATE SAMPLE DATA
# --------------------

@app.route("/create_players")
def create_players():

    p1 = Player(
        name="Virat Kohli",
        nationality="Indian",
        team="RCB",
        strike_rate=138.1,
        performance=9.5,
        current_bid=2000000
    )

    p2 = Player(
        name="Jos Buttler",
        nationality="Overseas",
        team="RR",
        strike_rate=145.3,
        performance=9.2,
        current_bid=1800000
    )

    db.session.add(p1)
    db.session.add(p2)

    db.session.commit()

    return "Players added"


if __name__ == "__main__":
    app.run()