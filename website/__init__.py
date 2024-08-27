from flask import Flask, session, jsonify, flash, render_template, current_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import OperationalError
from os import path
from flask_login import LoginManager, current_user
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from datetime import timedelta
from flask_security import Security, SQLAlchemyUserDatastore


import os
from dotenv import load_dotenv
import string
import random
# letters = string.ascii_lowercase
# my_secret_key = ( ''.join(random.choice(letters) for i in range(10)) )
load_dotenv()
# from flask_bcrypt import Bcrypt

db = SQLAlchemy()

DB_NAME = "../instance/"

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
bcrypt = Bcrypt()
mail = Mail()

def create_app():
    app = Flask(__name__)
    from flask_dance.contrib.google import make_google_blueprint, google
    from flask_dance.consumer import oauth_authorized
    
    google_blueprint = make_google_blueprint(
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    redirect_to="auth.google_login",
    scope=["profile", "email"]
    )
    app.register_blueprint(google_blueprint, url_prefix="/login")
    
    @app.errorhandler(OperationalError)
    def handle_operational_error(e):
        if "could not translate host name" in str(e):
            flash('Network connection error', category='success')
            return render_template("errors/500.html"), 500

            # return jsonify({"error": "Network connection error: Unable to resolve the database hostname."}), 503
        else:
            # return jsonify({"error": "Database error occurred."}), 500
            return render_template("errors/500.html"), 500
        
    app.config.update(
    SESSION_COOKIE_SECURE=True,  # Používajte len cez HTTPS
    SESSION_COOKIE_SAMESITE='None',  # Povoliť posielanie cookie cez domény
    )
    
    app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
    # app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("SQLALCHEMY_DATABASE_URI")
    app.config['SQLALCHEMY_POOL_SIZE'] = 10
    app.config['SQLALCHEMY_MAX_OVERFLOW'] = 5
    app.config['SQLALCHEMY_POOL_TIMEOUT'] = 30
    app.config['SQLALCHEMY_POOL_RECYCLE'] = 3600

    # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(DB_NAME, 'database.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("SQLALCHEMY_DATABASE_URI")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config['MAIL_SERVER'] = os.environ.get("MAIL_SERVER")
    app.config['MAIL_PORT'] = os.environ.get("MAIL_PORT")
    app.config['MAIL_USE_TLS'] = os.environ.get("MAIL_USE_TLS")
    app.config['MAIL_USERNAME'] = os.environ.get("MAIL_USERNAME")
    app.config['MAIL_PASSWORD'] = os.environ.get("MAIL_PASSWORD")
    app.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(minutes=60)
    # stripe.api_key = app.config['STRIPE_SECRET_KEY']

    # bcrypt = Bcrypt(app)

    # app.app_context().push()
    login_manager.init_app(app)
    db.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    
    from .views import views
    from .auth import auth
    from .products import products

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(products, url_prefix='/')
    
    # //////////////////////////only on production
    from website.errors.handlers import errors
    app.register_blueprint(errors)
    from flask import request, redirect
    # @app.before_request
    # def before_request():
    #     if request.url.startswith('http://'):
    #         url = request.url.replace('http://', 'https://', 1)
    #         return redirect(url, code=301)



    from .models import User, Note, Groupz, Duel
    
    
    @oauth_authorized.connect_via(google_blueprint)
    def google_logged_in(blueprint, token):
        if not token:
            flash("Failed to log in with Google.", category="error")
            return False

        resp = blueprint.session.get("/oauth2/v2/userinfo")
        if not resp.ok:
            flash("Failed to fetch user info from Google.", category="error")
            return False

        google_info = resp.json()
        google_user_id = google_info["id"]
        email = google_info["email"]
        name = google_info["name"]

        # Find or create user
        user = User.query.filter_by(email=email).first()
        if user is None:
            hashed_password = bcrypt.generate_password_hash("random_password").decode("utf-8")
            user = User(
                email=email,
                first_name=name,
                google_id=google_user_id,
                password=hashed_password
            )
            db.session.add(user)
            db.session.commit()

        login_user(user)
        flash("Successfully signed in with Google.", category="success")
        return False

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    
    from .models import User, Role
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    app.security = Security(app, user_datastore)
    
    from werkzeug.local import LocalProxy
    from functools import wraps
    _security = LocalProxy(lambda: current_app.extensions['security'])
    
    def roles_required(*roles):
        def wrapper(fn):
            @wraps(fn)
            def decorated_view(*args, **kwargs):
                if not current_user.is_authenticated:
                    return _security._unauthorized_callback()

                # Zmena tu: Skontroluje, či má užívateľ aspoň jednu z požadovaných rolí
                if any(current_user.has_role(role) for role in roles):
                    return fn(*args, **kwargs)
                else:
                    return "nonononono"
            return decorated_view
        return wrapper

    # @app.before_request
    # def before_request():
    #     if not request.is_secure:
    #         url = request.url.replace('http://', 'https://', 1)
    #         code = 301
    #         return redirect(url, code=code)
        
        
        
    return app



# def create_database(app):
#     if not path.exists(DB_NAME):
#         with app.app_context():
#             db.create_all()
#         print('Created Database!')

