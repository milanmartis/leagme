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
from celery import Celery
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
celery = None  # Initialize as None and configure later
cors = CORS()
csrf = CSRFProtect()

# Načítanie certifikátu zo súboru
cred = credentials.Certificate(os.environ.get("FIREBASE_URL_JSON"))

# Inicializácia aplikácie Firebase
firebase_admin.initialize_app(cred)

# Celery configuration
def make_celery(app=None):
    app = app or create_app()
    celery = Celery(
        app.import_name,
        broker=os.environ.get("CELERY_BROKER_URL"),
        backend=os.environ.get("CELERY_RESULT_BACKEND")
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
    app.config['CELERY_BROKER_URL'] = os.environ.get("CELERY_BROKER_URL")
    app.config['CELERY_RESULT_BACKEND'] = os.environ.get("CELERY_RESULT_BACKEND")
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
    cors.init_app(app, resources={r"/*": {"origins": "*"}}, 
                  allow_headers=["Authorization", "Content-Type"], 
                  methods=["GET", "POST", "OPTIONS"], 
                  supports_credentials=True)
    mail.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User, PushSubscription, ProductCategory, Product, Role, user_datastore

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

    # Firebase Messaging Example
    # def send_firebase_message(token, title, body):
    #     """Send a notification to a device using Firebase Cloud Messaging"""
    #     message = messaging.Message(
    #         notification=messaging.Notification(
    #             title=title,
    #             body=body
    #         ),
    #         token=token
    #     )
    #     response = messaging.send(message)
    #     print(f"Successfully sent message: {response}")

    # # Role Protection Definition
    # _security = LocalProxy(lambda: current_app.extensions['security'])

    # Zoznam subscription údajov a FCM tokenov
    subscriptions = []
    fcm_tokens = []

    # Endpoint pre získanie Firebase konfigurácie
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

    # Route na odoslanie subscription údajov na backend
    @app.route('/subscribe', methods=['POST'])
    def subscribe():
        subscription_data = request.get_json()

        # Získaj informácie o používateľovi, napr. aktuálne prihláseného používateľa
        user_id = current_user.id if current_user.is_authenticated else None

        # Skontroluj, či sa jedná o FCM token alebo Web Push subscription
        if 'token' in subscription_data:
            # Spracovanie FCM tokenu (pre iOS zariadenia)
            fcm_token = subscription_data['token']
            print(fcm_token)

            # Skontroluj, či už FCM token existuje v databáze
            existing_fcm_token = PushSubscription.query.filter_by(auth=fcm_token).first()

            if not existing_fcm_token:
                # Vytvor nové FCM subscription pre iOS
                new_fcm_subscription = PushSubscription(
                    user_id=user_id,
                    endpoint=None,  # FCM token nemá endpoint
                    p256dh=None,    # FCM token nemá p256dh kľúč
                    auth=fcm_token  # Ulož FCM token do auth stĺpca
                )
                db.session.add(new_fcm_subscription)
                db.session.commit()
                return jsonify({'message': 'FCM token uložený úspešne.'}), 201
            else:
                return jsonify({'message': 'FCM token už existuje.'}), 200

        else:
            # Spracovanie Web Push subscription (pre ostatné zariadenia)
            endpoint = subscription_data['endpoint']
            p256dh = subscription_data['keys']['p256dh']
            auth = subscription_data['keys']['auth']

            # Skontroluj, či už Web Push subscription existuje v databáze
            existing_subscription = PushSubscription.query.filter_by(endpoint=endpoint).first()

            if not existing_subscription:
                # Vytvor nové Web Push subscription
                new_subscription = PushSubscription(
                    user_id=user_id,
                    endpoint=endpoint,
                    p256dh=p256dh,
                    auth=auth
                )
                db.session.add(new_subscription)
                db.session.commit()
                return jsonify({'message': 'Web Push subscription uložené úspešne.'}), 201
            else:
                return jsonify({'message': 'Web Push subscription už existuje.'}), 200

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



    @app.route('/send_test_notification', methods=['POST'])
    def send_test_notification():
        # Definovanie notifikácie, ktorú chceme poslať
        notification_payload = {
            "title": "Skúšobná notifikácia",
            "body": "Toto je test push notifikácie",
            "icon": "/static/img/icon.png"
        }

        # Načítanie všetkých subscription z databázy
        subscriptions = PushSubscription.query.all()

        if not subscriptions:
            return jsonify({"message": "Nie sú uložené žiadne predplatné (subscriptions)"}), 400

        # Posielanie Web Push notifikácií pre všetky uložené subscriptions
        for subscription in subscriptions:
            try:
                # Získaj endpoint z databázy
                endpoint = subscription.endpoint

                # Dynamické získanie audience (na základe endpointu)
                audience = get_audience_from_subscription(endpoint)

                # Nastavenie VAPID claimov s dynamickým audience
                vapid_claims = {
                    "sub": "mailto:tvoj-email@example.com",
                    "aud": audience
                }

                # Posielanie push notifikácie pomocou webpush
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
                if ex.response:
                    print(f"Detailná odpoveď zo servera: Status kód: {ex.response.status_code}, Text: {ex.response.text}")
                return jsonify({"message": "Chyba pri odoslaní Web Push notifikácie2"}), 500
            except ValueError as ve:
                print(f"Chyba: {ve}")
                return jsonify({"message": f"Chyba: {ve}"}), 400

        return jsonify({"message": "Notifikácia bola úspešne odoslaná všetkým používateľom"}), 200

    
    
    @app.route('/send_notification', methods=['POST'])
    def send_notification():
        # Príklad payloadu pre notifikáciu
        notification_payload = {
            "title": "Nové oznámenie",
            "body": "Máš nové oznámenie",
            "icon": "/static/img/icon.png"
        }

        # Získaj všetky subscription z databázy
        subscriptions = PushSubscription.query.all()

        for subscription in subscriptions:
            try:
                # Odošli push notifikáciu
                webpush(
                    subscription_info={
                        "endpoint": subscription.endpoint,
                        "keys": {
                            "p256dh": subscription.p256dh,
                            "auth": subscription.auth
                        }
                    },
                    data=json.dumps(notification_payload),
                    vapid_private_key=os.environ.get('VAPID_PRIVATE_KEY'),
                    vapid_claims={
                        "sub": "mailto:example@example.com"
                    }
                )
            except WebPushException as ex:
                print(f"Chyba pri odosielaní notifikácie: {ex}")
                # Ak je subscription neplatná, môžeme ju odstrániť
                if ex.response and ex.response.status_code == 410:
                    db.session.delete(subscription)
                    db.session.commit()

        return jsonify({'message': 'Notifikácie odoslané.'}), 200

    # Route na odosielanie push notifikácií
    # @app.route('/send_notification', methods=['POST'])
    # def send_notification():
    #     notification_payload = {
    #         "title": "Nová správa",
    #         "body": "Toto je ukážka push notifikácie",
    #         "icon": "/path-to-icon.png"
    #     }
    #     for subscription in subscriptions:
    #         try:
    #             webpush(
    #                 subscription_info=subscription,
    #                 data=json.dumps(notification_payload),
    #                 vapid_private_key=os.environ.get("VAPID_PRIVATE_KEY"),
    #                 vapid_claims=vapid_claims
    #             )
    #         except WebPushException as ex:
    #             print(f"Error sending notification: {ex}")
    #             return jsonify({"message": "Error sending notification"}), 500

    #     return jsonify({"message": "Notifications sent"}), 200
    
    # @app.route('/get-firebase-config')
    # def get_firebase_config():
    #     config = {
    #         "apiKey": os.environ.get("FIREBASE_API_KEY"),
    #         "authDomain": os.environ.get("FIREBASE_AUTH_DOMAIN"),
    #         "projectId": os.environ.get("FIREBASE_PROJECT_ID"),
    #         "storageBucket": os.environ.get("FIREBASE_STORAGE_BUCKET"),
    #         "messagingSenderId": os.environ.get("FIREBASE_MESSAGING_SENDER_ID"),
    #         "appId": os.environ.get("FIREBASE_APP_ID"),
    #         "measurementId": os.environ.get("FIREBASE_MEASUREMENT_ID")
    #     }
    #     return jsonify(config)

    # @app.route('/send-notification', methods=['POST'])
    # def send_notification():
    #     data = request.get_json()
    #     token = data.get('token')
    #     title = data.get('title')
    #     body = data.get('body')

    #     # Odoslanie notifikácie cez Firebase Messaging
    #     message = messaging.Message(
    #         notification=messaging.Notification(
    #             title=title,
    #             body=body
    #         ),
    #         token=token
    #     )
    #     response = messaging.send(message)
    #     return jsonify({"message": "Notification sent", "response": response})

    # @app.route('/vapid-public-key')
    # def get_vapid_public_key():
    #     vapid_public_key=os.getenv("VAPID_PUBLIC_KEY")
    #     return jsonify({'publicKey': vapid_public_key})
    
    @app.route('/vapid-public-key')
    def get_public_vapid_key():
        public_vapid_key = os.getenv('VAPID_PUBLIC_KEY')
        return jsonify({"publicVapidKey": public_vapid_key})

    @app.route('/firebase-messaging-sw.js')
    def service_worker():
        return send_from_directory('static', 'firebase-messaging-sw.js')
    


    @app.template_filter('datetimeformat')
    def datetimeformat(value, format='%d/%m/%Y'):
        return datetime.fromtimestamp(value).strftime(format)

    @app.route('/notify-disconnect', methods=['POST'])
    def notify_disconnect():
        data = request.get_json()
        message = data.get('message', 'An unknown issue occurred.')

        # Použijeme flash správu na upozornenie používateľa
        flash(message, category='error')

        return jsonify({'status': 'success', 'message': 'Notification received'}), 200

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        return jsonify({'error': 'CSRF token missing or incorrect.'}), 400

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
