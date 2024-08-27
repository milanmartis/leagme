from flask import Flask, session, jsonify, flash, render_template, current_app
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

# Načítanie environmentálnych premenných
load_dotenv()

# Inicializácia rozšírení
db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
mail = Mail()

def create_app():
    app = Flask(__name__)

    # Konfigurácia aplikácie
    app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("SQLALCHEMY_DATABASE_URI")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config['SQLALCHEMY_POOL_SIZE'] = 10
    app.config['SQLALCHEMY_MAX_OVERFLOW'] = 5
    app.config['SQLALCHEMY_POOL_TIMEOUT'] = 30
    app.config['SQLALCHEMY_POOL_RECYCLE'] = 3600
    app.config['MAIL_SERVER'] = os.environ.get("MAIL_SERVER")
    app.config['MAIL_PORT'] = os.environ.get("MAIL_PORT")
    app.config['MAIL_USE_TLS'] = os.environ.get("MAIL_USE_TLS")
    app.config['MAIL_USERNAME'] = os.environ.get("MAIL_USERNAME")
    app.config['MAIL_PASSWORD'] = os.environ.get("MAIL_PASSWORD")
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=60)
    app.config.update(
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_SAMESITE='None',
    )

    # Inicializácia rozšírení s aplikáciou
    db.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # Import a registrácia blueprintov
    from .views import views
    from .auth import auth
    from .products import products
    from .errors.handlers import errors

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(products, url_prefix='/')
    app.register_blueprint(errors)

    # Registrácia Google OAuth blueprintu
    google_blueprint = make_google_blueprint(
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        redirect_to="auth.google_login",
        scope=["profile", "email"]
    )
    app.register_blueprint(google_blueprint, url_prefix="/login")

    # Inicializácia Flask-Security
    from .models import User, Role
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    Security(app, user_datastore)

    # Definícia ochrany rolí
    _security = LocalProxy(lambda: current_app.extensions['security'])

    def roles_required(*roles):
        def wrapper(fn):
            @wraps(fn)
            def decorated_view(*args, **kwargs):
                if not current_user.is_authenticated:
                    return _security._unauthorized_callback()
                if any(current_user.has_role(role) for role in roles):
                    return fn(*args, **kwargs)
                else:
                    return "nonononono"
            return decorated_view
        return wrapper

    # Handler pre chyby databázy
    @app.errorhandler(OperationalError)
    def handle_operational_error(e):
        if "could not translate host name" in str(e):
            flash('Network connection error', category='error')
            return render_template("errors/500.html"), 500
        return render_template("errors/500.html"), 500

    # Funkcia na načítanie užívateľa
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app
