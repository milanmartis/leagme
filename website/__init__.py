from flask import Flask, session, jsonify, flash, render_template, current_app, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import OperationalError
from flask_login import LoginManager, current_user, login_user, logout_user
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from datetime import timedelta, datetime
from flask_security import Security, SQLAlchemyUserDatastore
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.consumer import oauth_authorized
from dotenv import load_dotenv
import os
from functools import wraps
from werkzeug.local import LocalProxy
from flask_argon2 import Argon2
from flask_socketio import SocketIO, emit, join_room, leave_room
from redis import Redis
from celery import Celery
from flask_session import Session
from flask_caching import Cache  # Import Cache

import uuid

# Load environment variables
load_dotenv()
# os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
mail = Mail()
argon2 = Argon2()
socketio = SocketIO()
cache = Cache()
celery = None  # Initialize as None and configure later

def make_celery(app=None):
    app = app or create_app()
    celery = Celery(
        app.import_name,
        broker='redis://elasticacheleagme-wb2hf0.serverless.eun1.cache.amazonaws.com:6379/0',  # Redis endpoint from ElastiCache
        backend='redis://elasticacheleagme-wb2hf0.serverless.eun1.cache.amazonaws.com:6379/0'  # Redis as backend
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

def create_app():
    app = Flask(__name__)

    # Application Configuration
    app.config["DEBUG"] = False
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
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
    app.config['SESSION_TYPE'] = 'redis'
    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_USE_SIGNER'] = True
    app.config['SESSION_REDIS'] = Redis(host=os.environ.get("SESSION_REDIS"), port=6379)
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=60)
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=5)
    app.config['CELERY_BROKER_URL'] = os.environ.get("CELERY_BROKER_URL")
    app.config['CELERY_RESULT_BACKEND'] = os.environ.get("CELERY_RESULT_BACKEND")
    app.config['CACHE_TYPE'] = 'redis'
    app.config['CACHE_REDIS_URL'] = os.environ.get("CACHE_REDIS_URL")

    # cache.init_app(app) 
    cache.init_app(app, config={'CACHE_TYPE': 'redis'})  # alebo iný typ cache
    db.init_app(app)
    bcrypt.init_app(app)
    argon2.init_app(app)
    mail.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)


    from .models import User, Role, user_datastore

    # Configure Google OAuth Blueprint
    google_blueprint = make_google_blueprint(
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        redirect_to="views.index",  # Function to handle the redirection after login
        scope=["openid", "https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile"]
    )
    app.register_blueprint(google_blueprint, url_prefix="/login")

    # OAuth Authorized Handler
    @oauth_authorized.connect_via(google_blueprint)
    def google_logged_in(blueprint, token):
        if not token:
            flash("Failed to log in with Google.", category="error")
            return False

        resp = google.get("/oauth2/v1/userinfo")
        if not resp.ok:
            flash("Failed to fetch user info from Google.", category="error")
            return False

        user_info = resp.json()
        user_email = user_info["email"]

        # Check if user already exists
        user = User.query.filter_by(email=user_email).first()
        if not user:
            # If not, create a new user
            user = User(
                email=user_email, 
                first_name=user_info.get("email"),
                authenticated=True, 
                confirm=True, 
                active=True, 
                fs_uniquifier=str(uuid.uuid4()))
            db.session.add(user)
            db.session.commit()

        login_user(user)
        flash("Successfully signed in with Google.", category="success")
        return redirect(url_for("views.index"))

    # Initialize Celery after app is created
    global celery
    celery = make_celery(app)

    # socketio.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*", async_mode="gevent")

    # Register Blueprints
    from .views import views
    from .auth import auth
    from .products import products
    from .errors.handlers import errors

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(products, url_prefix='/')
    app.register_blueprint(errors)

    # Initialize Flask-Security
    Security(app, user_datastore)

    # Role Protection Definition
    _security = LocalProxy(lambda: current_app.extensions['security'])

    @app.template_filter('datetimeformat')
    def datetimeformat(value, format='%d/%m/%Y'):
        return datetime.fromtimestamp(value).strftime(format)
    
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
