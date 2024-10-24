from flask import Flask, session, jsonify, flash, render_template, current_app, redirect, url_for, request, send_from_directory
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
from flask_session import Session
from flask_caching import Cache
from flask_cors import CORS
from flask_wtf.csrf import CSRFProtect, CSRFError
import uuid
import json
import boto3
import firebase_admin
from firebase_admin import credentials, firestore, auth, messaging, initialize_app
from pywebpush import webpush, WebPushException
from lambda_functions import lambda_handler  # Importuješ Lambda handler

import requests
import traceback

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
mail = Mail()
argon2 = Argon2()
socketio = SocketIO()
cache = Cache()
cors = CORS()
csrf = CSRFProtect()

# Načítanie certifikátu zo súboru alebo obsahu
firebase_credentials = os.environ.get("FIREBASE_URL_JSON")
if firebase_credentials:
    cred = credentials.Certificate(firebase_credentials)
    firebase_admin.initialize_app(cred)


def create_app():
    app = Flask(__name__)

    # Application Configuration
    app.config["DEBUG"] = False
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
    app.config["SECURITY_PASSWORD_SALT"] = "156043940537155509276282232127182067465"
    app.config["SECURITY_TOTP_SECRETS"] = {"1": "TjQ9Qa31VOrfEzuPy4VHQWPCTmRzCnFzMKLxXYiZu9B"}
    app.config["SECURITY_PASSWORD_HASH"] = "argon2"
    app.config['SECURITY_CONFIRMABLE'] = True
    app.config['SECURITY_REGISTERABLE'] = True
    app.config['SECURITY_RECOVERABLE'] = True
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
    app.config['CACHE_TYPE'] = 'redis'
    app.config['CACHE_REDIS_URL'] = os.environ.get("CACHE_REDIS_URL")
    app.config['VAPID_PUBLIC_KEY'] = os.environ.get("VAPID_PUBLIC_KEY")
    app.config['VAPID_PRIVATE_KEY'] = os.environ.get("VAPID_PRIVATE_KEY")

    # Initialize extensions
    cache.init_app(app, config={'CACHE_TYPE': 'redis'})
    db.init_app(app)
    csrf.init_app(app)
    bcrypt.init_app(app)
    argon2.init_app(app)
    cors.init_app(app, resources={r"/*": {"origins": "*"}}, allow_headers=["Authorization", "Content-Type"], methods=["GET", "POST", "OPTIONS"], supports_credentials=True)
    mail.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    
    from .models import User, Round, PushSubscription, ProductCategory, Product, Role, user_datastore



    # Configure Google OAuth Blueprint
    google_blueprint = make_google_blueprint(
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        redirect_to="views.index",
        scope=["openid", "https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile"]
    )
    app.register_blueprint(google_blueprint, url_prefix="/login")

    # OAuth Authorized Handler
    @oauth_authorized.connect_via(google_blueprint)
    def google_logged_in(blueprint, token):
        if not token:
            flash("Failed to log in with Google.", category="error")
            return False

        resp = google.get("/oauth2/v2/userinfo")
        if not resp.ok:
            flash("Failed to fetch user info from Google.", category="error")
            return False

        user_info = resp.json()
        user_email = user_info["email"]

        # Check if user already exists
        user = User.query.filter_by(email=user_email).first()
        if not user:
            user = User(
                email=user_email,
                first_name=user_info.get("email"),
                authenticated=True,
                confirm=True,
                active=True,
                fs_uniquifier=str(uuid.uuid4())
            )
            db.session.add(user)
            db.session.commit()

        login_user(user)
        flash("Successfully signed in with Google.", category="success")
        return redirect(url_for("views.index"))

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
    
    
    @app.route('/invoke_lambda', methods=['GET'])
    def invoke_lambda():
        # Simuluješ Lambda event pre úlohu "close_rounds"
        event = {"task": "close_rounds"}
        result = lambda_handler(event, None)
        return jsonify(result)


    # Firebase Messaging Example
    @app.route('/get-firebase-config', methods=['GET'])
    def get_firebase_config():
        firebase_config = {
            "apiKey": os.environ.get('FIREBASE_API_KEY'),
            "authDomain": os.environ.get('FIREBASE_AUTH_DOMAIN'),
            "projectId": os.environ.get('FIREBASE_PROJECT_ID'),
            "storageBucket": os.environ.get('FIREBASE_STORAGE_BUCKET'),
            "messagingSenderId": os.environ.get('FIREBASE_MESSAGING_SENDER_ID'),
            "appId": os.environ.get('FIREBASE_APP_ID'),
            "measurementId": os.environ.get('FIREBASE_MEASUREMENT_ID')
        }
        return jsonify(firebase_config)

    # Subscription routes for Push Notifications
    @app.route('/subscribe', methods=['POST'])
    def subscribe():
        subscription_data = request.get_json()
        user_id = current_user.id if current_user.is_authenticated else None
        device_type = subscription_data.get('deviceType', 'Unknown')
        operating_system = subscription_data.get('operatingSystem', 'Unknown')
        browser_name = subscription_data.get('browserName', 'Unknown')

        # Handle FCM token subscriptions for iOS
        if 'token' in subscription_data:
            fcm_token = subscription_data['token']
            existing_fcm_tokens = PushSubscription.query.filter_by(
                user_id=user_id,
                device_type=device_type,
                operating_system=operating_system,
                browser_name=browser_name
            ).all()

            for subscription in existing_fcm_tokens:
                if subscription.auth != fcm_token:
                    db.session.delete(subscription)
            db.session.commit()

            if not any(sub.auth == fcm_token for sub in existing_fcm_tokens):
                new_fcm_subscription = PushSubscription(
                    user_id=user_id,
                    auth=fcm_token,
                    device_type=device_type,
                    operating_system=operating_system,
                    browser_name=browser_name
                )
                db.session.add(new_fcm_subscription)
                db.session.commit()
                return jsonify({'message': 'FCM token uložený úspešne.'}), 201
            else:
                return jsonify({'message': 'FCM token už existuje.'}), 200

        else:
            # Handle Web Push subscriptions
            endpoint = subscription_data['subscription']['endpoint']
            p256dh = subscription_data['subscription']['keys']['p256dh']
            auth = subscription_data['subscription']['keys']['auth']
            existing_subscriptions = PushSubscription.query.filter_by(
                user_id=user_id,
                device_type=device_type,
                operating_system=operating_system,
                browser_name=browser_name
            ).all()

            for subscription in existing_subscriptions:
                if subscription.endpoint != endpoint or subscription.auth != auth:
                    db.session.delete(subscription)
            db.session.commit()

            if not any(sub.endpoint == endpoint and sub.auth == auth for sub in existing_subscriptions):
                new_subscription = PushSubscription(
                    user_id=user_id,
                    endpoint=endpoint,
                    p256dh=p256dh,
                    auth=auth,
                    device_type=device_type,
                    operating_system=operating_system,
                    browser_name=browser_name
                )
                db.session.add(new_subscription)
                db.session.commit()
                return jsonify({'message': 'Web Push subscription uložené úspešne.'}), 201
            else:
                return jsonify({'message': 'Web Push subscription už existuje.'}), 200

    @app.route('/check-subscription', methods=['GET'])
    def check_subscription():
        user_id = request.args.get('user_id')
        device_type = request.args.get('device_type')
        operating_system = request.args.get('operating_system')
        browser_name = request.args.get('browser_name')

        if not user_id:
            return jsonify({'error': 'Žiadny user nebol najdeny.'}), 400

        existing_subscription = PushSubscription.query.filter_by(
            user_id=user_id,
            device_type=device_type,
            operating_system=operating_system,
            browser_name=browser_name
        ).first()

        if existing_subscription:
            return jsonify({'subscribed': True}), 200
        else:
            return jsonify({'subscribed': False}), 200

    # Unsubscribe endpoint
    @app.route('/unsubscribe', methods=['POST'])
    def unsubscribe():
        subscription_data = request.get_json()
        user_id = subscription_data.get('user_id')
        device_type = subscription_data.get('device_type')
        operating_system = subscription_data.get('operating_system')
        browser_name = subscription_data.get('browser_name')

        try:
            subscriptions = PushSubscription.query.filter_by(
                user_id=user_id,
                device_type=device_type,
                operating_system=operating_system,
                browser_name=browser_name
            ).all()

            for subscription in subscriptions:
                db.session.delete(subscription)
            db.session.commit()

            return jsonify({'message': 'Predplatné bolo vymazané.'}), 200
        except Exception as e:
            print('Error:', e)
            return jsonify({'message': 'Chyba servera.'}), 500
        
        
        # Dynamicky nastavíme audience podľa subscription endpointu
    def get_audience_from_subscription(endpoint):
        if "fcm.googleapis.com" in endpoint:
            return "https://fcm.googleapis.com"
        elif "push.services.mozilla.com" in endpoint:
            return "https://updates.push.services.mozilla.com"
        elif "notify.windows.com" in endpoint:
            return "https://wns.windows.com"
        elif "web.push.apple.com" in endpoint:
            return "https://web.push.apple.com"
        elif "push.opera.com" in endpoint:
            return "https://push.opera.com"
        else:
            raise ValueError(f"Neznámy push server pre endpoint: {endpoint}")


    from firebase_admin import messaging

    def send_push_notification(token, title, body):
        """Odoslanie push notifikácie na dané zariadenie pomocou FCM."""
        
        # Vytvorenie správy
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            token=token,  # Toto je token zariadenia, kam notifikáciu posielate
        )

        # Odoslanie správy
        try:
            response = messaging.send(message)
            print('Úspešne odoslané:', response)
        except Exception as e:
            print('Chyba pri odosielaní notifikácie:', e)

    @app.route('/send_test_notification', methods=['POST'])
    def send_test_notification():
        notification_payload = {
            "title": "Skúšobná notifikácia",
            "body": "Toto je test push notifikácie",
            "icon": "/static/img/icon.png"
        }
        subscriptions = PushSubscription.query.all()

        for subscription in subscriptions:
            if subscription.operating_system == 'MacOS':
                send_push_notification(subscription.auth, 'title', 'body')
            else:
                try:
                    endpoint = subscription.endpoint
                    audience = get_audience_from_subscription(endpoint)
                    vapid_claims = {
                        "sub": "mailto:tvoj-email@example.com",
                        "aud": audience
                    }
                    webpush(
                        subscription_info={
                            "endpoint": subscription.endpoint,
                            "keys": {
                                "p256dh": subscription.p256dh,
                                "auth": subscription.auth
                            }
                        },
                        data=json.dumps(notification_payload),
                        vapid_private_key=os.environ.get("VAPID_PRIVATE_KEY"),
                        vapid_claims=vapid_claims
                    )
                except WebPushException as ex:
                    print(f"Chyba pri posielaní Web Push notifikácie: {ex}")
                    return jsonify({"message": "Chyba pri odoslaní Web Push notifikácie"}), 500
                except ValueError as ve:
                    print(f"Chyba: {ve}")
                    return jsonify({"message": f"Chyba: {ve}"}), 400

        return jsonify({"message": "Notifikácia bola úspešne odoslaná všetkým používateľom"}), 200

    # # Celery periodic task example
    # @celery.task
    # def check_and_close_rounds_task():
    #     current_time = datetime.now()
    #     open_rounds = Round.query.filter_by(open=True).all()

    #     for round_instance in open_rounds:
    #         round_end_time = round_instance.round_start + timedelta(seconds=round_instance.duration)
    #         if current_time >= round_end_time:
    #             round_instance.open = False
    #             db.session.add(round_instance)
    #             db.session.commit()

    #     return "Closed all open rounds after limit"

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        print("CSRF Error: ", e.description)
        return jsonify({'error': 'CSRF token missing or incorrect.'}), 400

    @app.errorhandler(OperationalError)
    def handle_operational_error(e):
        if "could not translate host name" in str(e):
            flash('Network connection error', category='error')
            return render_template("errors/500.html"), 500
        return render_template("errors/500.html"), 500

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app