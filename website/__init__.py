from flask import Flask, session, jsonify, flash, render_template, current_app, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import OperationalError
from flask_login import LoginManager, current_user
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from datetime import timedelta
from flask_security import Security, SQLAlchemyUserDatastore
from flask_dance.contrib.google import make_google_blueprint
from flask_dance.consumer import oauth_authorized
from dotenv import load_dotenv
import os
from functools import wraps
from werkzeug.local import LocalProxy
from flask_argon2 import Argon2

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
mail = Mail()
argon2 = Argon2()
def create_app():
    app = Flask(__name__)

    # Application Configuration
    app.config["DEBUG"] = True
    app.config["SECRET_KEY"] = "pf9Wkove4IKEAXvy-cQkeDPhv9Cb3Ag-wyJILbq_dFw"
    app.config["SECURITY_PASSWORD_SALT"] = "156043940537155509276282232127182067465"
    app.config["SECURITY_TOTP_SECRETS"] = {"1": "TjQ9Qa31VOrfEzuPy4VHQWPCTmRzCnFzMKLxXYiZu9B"}
    app.config["SECURITY_PASSWORD_HASH"] = "argon2"  # Set Argon2 as the default hash
    app.config['SECURITY_CONFIRMABLE'] = True  # Enables email confirmation
    app.config['SECURITY_REGISTERABLE'] = True  # Allows user registration
    app.config['SECURITY_RECOVERABLE'] = True   # Enables password recovery
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("SQLALCHEMY_DATABASE_URI")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config['MAIL_SERVER'] = os.environ.get("MAIL_SERVER")
    app.config['MAIL_PORT'] = os.environ.get("MAIL_PORT")
    app.config['MAIL_USE_TLS'] = os.environ.get("MAIL_USE_TLS")
    app.config['MAIL_USERNAME'] = os.environ.get("MAIL_USERNAME")
    app.config['MAIL_PASSWORD'] = os.environ.get("MAIL_PASSWORD")
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=60)
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=5)

    # Initialize extensions with app
    db.init_app(app)
    bcrypt.init_app(app)
    argon2.init_app(app)
    mail.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    # Register Blueprints
    from .views import views
    from .auth import auth
    from .products import products
    from .errors.handlers import errors

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(products, url_prefix='/')
    app.register_blueprint(errors)

    # Google OAuth Blueprint
    # Definícia Google blueprintu musí byť pred použitím v dekorátore

    google_blueprint = make_google_blueprint(
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        redirect_to="auth.google_login",
        scope=["profile", "email"]
    )
    app.register_blueprint(google_blueprint, url_prefix="/login")

    # Registrácia blueprintov
    # from .auth import auth as auth_blueprint
    # app.register_blueprint(auth_blueprint)
    
    
    # Initialize Flask-Security
    from .models import User, Role, user_datastore
    Security(app, user_datastore)

    # Role Protection Definition
    _security = LocalProxy(lambda: current_app.extensions['security'])



    
    # Error Handler for Database Issues
    @app.errorhandler(OperationalError)
    def handle_operational_error(e):
        if "could not translate host name" in str(e):
            flash('Network connection error', category='error')
            return render_template("errors/500.html"), 500
        return render_template("errors/500.html"), 500

    # User Loader Function for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app
