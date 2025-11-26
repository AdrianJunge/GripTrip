import os
import urllib.parse
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager

class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)

VIRT_LAB_DB = os.environ.get("VIRT_LAB_DB", "0") == "1"

def create_app(test_config=None):
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")

    if VIRT_LAB_DB:
      DB_USER = "26_webapp_24"
      DB_PASSWORD = "byUsC1YJ"
      DB_HOST = "mysql.lab.it.uc3m.es"
      DB_NAME = f'{DB_USER}a'

      app.config[
          "SQLALCHEMY_DATABASE_URI"
      ] = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
    else:
      DB_USER = os.environ.get("DB_USER", "webapp")
      DB_PASSWORD = os.environ.get("DB_PASSWORD", "webapp-user")
      DB_HOST = os.environ.get("DB_HOST", "127.0.0.1")
      DB_PORT = os.environ.get("DB_PORT", "3306")
      DB_NAME = os.environ.get("DB_NAME", "web_app")

      password_quoted = urllib.parse.quote_plus(DB_PASSWORD)

      app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{DB_USER}:{password_quoted}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
      app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    from . import model

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(model.User, int(user_id))

    from . import main, auth, profile, trip
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(profile.bp)
    app.register_blueprint(trip.bp)

    from .const import NOTIFICATION_TYPES
    @app.context_processor
    def inject_notification_types():
      return {"NOTIFICATION_TYPES": NOTIFICATION_TYPES}

    return app
