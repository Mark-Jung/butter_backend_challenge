import os
from flask import Flask
from flask_cors import CORS
from cache import cache
from db import db

app = Flask(__name__)
uri = os.environ.get("DATABASE_URL", "sqlite:///localdata.db")
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "my_secret")

cache.init_app(app)


from views.PingView import PingView
from views.LoadView import LoadView
from views.AuthorizationView import AuthorizationView


@app.route("/ping", methods=["GET"])
def ping():
    return PingView.ping()

@app.route("/load/<string:messageId>", methods=["PUT"])
def load_credit(messageId):
    return LoadView.load_credit(messageId)

@app.route("/authorization/<string:messageId>", methods=["PUT"])
def authorize_debit(messageId):
    return AuthorizationView.authorize_debit(messageId)

if __name__ == "__main__":
    CORS(app)
    app.debug = True
    db.init_app(app)
    with app.app_context():
        db.create_all()
    app.run()

    """
    seeder = Seeder(app.app_context())
    seeder.seed()
    """