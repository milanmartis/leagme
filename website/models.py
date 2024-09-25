from website import db
from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer
from flask_security import RoleMixin, SQLAlchemyUserDatastore
from flask_security.models import fsqla_v3 as fsqla
from flask_security.utils import hash_password, verify_and_update_password
from sqlalchemy.sql import func
from sqlalchemy import PrimaryKeyConstraint
from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from datetime import datetime

# from flask_babel import gettext as _

roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
                       db.Column('role_id', db.Integer(), db.ForeignKey('role.id')),
                       db.UniqueConstraint('user_id', 'role_id', name='unique_user_role'))

user_duel = db.Table('user_duel',
                     db.Column('user_id', db.Integer, db.ForeignKey('user.id', onupdate="CASCADE", ondelete="CASCADE")),
                     db.Column('duel_id', db.Integer, db.ForeignKey('duel.id', onupdate="CASCADE", ondelete="CASCADE")),
                     db.Column('result', db.Integer, default=0),
                     db.Column('against', db.Integer, default=0),
                     db.Column('points', db.Integer, default=0),
                     db.Column('checked', db.String(10), default="false"),
                     db.Column('notez', db.Integer),
                     db.Column('addons', db.Integer, default=1))

user_group = db.Table('user_group',
                      db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                      db.Column('groupz_id', db.Integer, db.ForeignKey('groupz.id', ondelete="CASCADE")),
                      db.Column('season_id', db.Integer, db.ForeignKey('season.id', ondelete="CASCADE")),
                      db.Column('round_id', db.Integer, db.ForeignKey('round.id')),
                      db.Column('duel_id', db.Integer, db.ForeignKey('duel.id')))

user_season = db.Table('user_season',
                       db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                       db.Column('season_id', db.Integer, db.ForeignKey('season.id')),
                       db.Column('season_first_date', db.DateTime(timezone=True), default=func.now()),
                       db.Column('orderz', db.Integer))



class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    data = db.Column(db.String(10000))
    date_time = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Groupz(db.Model):
    __tablename__ = 'groupz'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(300))
    shorts = db.Column(db.Text)
    season_id = db.Column(db.Integer, db.ForeignKey('season.id', ondelete="CASCADE"))
    round_id = db.Column(db.Integer, db.ForeignKey('round.id', ondelete="CASCADE"))

class User(db.Model, fsqla.FsUserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(255))  # Increased length for compatibility with Flask-Security
    first_name = db.Column(db.String(150))
    username = db.Column(db.String(64))
    google_id = db.Column(db.String(100), unique=True)
    # messages = db.relationship('Message', backref='user')
    orderz = db.Column(db.Integer)
    notes = db.relationship('Note')
    seasony = db.relationship('Season', secondary=user_season, backref=db.backref('seasons'))
    groupy = db.relationship('Groupz', secondary=user_group, backref='groups')
    play = db.relationship('Duel', secondary=user_duel, backref='players')
    authenticated = db.Column(db.Boolean, default=False)
    confirm = db.Column(db.Boolean, default=False)
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))
    stripe_subscription_id = db.Column(db.String(255), unique=True, nullable=True)
    fs_uniquifier = db.Column(db.String(64), unique=True, nullable=False)
    active = db.Column(db.Boolean, default=True)
    confirmed_at = db.Column(db.DateTime)
    last_login_at = db.Column(db.DateTime())
    current_login_at = db.Column(db.DateTime())
    last_login_ip = db.Column(db.String(100))
    current_login_ip = db.Column(db.String(100))
    login_count = db.Column(db.Integer, default=0)
    tf_primary_method = db.Column(db.String(255))
    tf_totp_secret = db.Column(db.String(255))
    tf_phone_number = db.Column(db.String(20))
    fs_webauthn_user_handle = db.Column(db.String(64), unique=True, nullable=True)
    mf_recovery_codes = db.Column(db.String(256), nullable=True)
    us_phone_number = db.Column(db.String(64), nullable=True)
    us_totp_secrets = db.Column(db.String(256), nullable=True)
    create_datetime = db.Column(db.DateTime, default=func.now())
    update_datetime = db.Column(db.DateTime, default=func.now(), onupdate=func.now())

    def get_reset_token(self):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id})

    def get_confirm_token(self):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id})

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(int(user_id))

    @staticmethod
    def verify_confirm_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(int(user_id))

    def __repr__(self):
        return f"User('{self.first_name}', '{self.email}', '{self.roles}', '{self.seasony}', '{self.stripe_subscription_id}')"

    def has_roles(self, *args):
        return set(args).issubset({role.name for role in self.roles})

class Role(db.Model, fsqla.FsRoleMixin):
    __tablename__ = 'role'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(180), unique=True)
    description = db.Column(db.String(255))
    permissions = db.Column(db.String(255))
    update_datetime = db.Column(db.DateTime)

class Round(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    season_id = db.Column(db.Integer, db.ForeignKey('season.id', ondelete="CASCADE"))
    round_start = db.Column(db.DateTime(timezone=True), default=func.now())
    open = db.Column(db.Boolean(), default=True)
    duration = db.Column(db.Integer)

class Season(db.Model):
    __tablename__ = 'season'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300), unique=True)
    min_players = db.Column(db.Integer)
    no_group = db.Column(db.Integer)
    no_round = db.Column(db.Integer)
    winner_points = db.Column(db.Integer)
    visible = db.Column(db.Boolean(), default=False)
    season_type = db.Column(db.Integer)
    season_end_round = db.Column(db.Integer)
    open = db.Column(db.Boolean(), default=False)
    season_from = db.Column(db.DateTime(timezone=True))
    season_to = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    place_id = db.Column(db.Integer, db.ForeignKey('place.id'), nullable=True)  # Pridanie stĺpca place_id

    # Vzťahy
    place = db.relationship('Place', backref='seasons')
    
class Place(db.Model):
    __tablename__ = 'place'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300))
    slug = db.Column(db.String(300), unique=True, nullable=False)  # Slug field
    address_street = db.Column(db.String(300))
    address_street_no = db.Column(db.String(50))
    address_street_zip = db.Column(db.String(20))
    address_street_city = db.Column(db.String(100))
    address_street_state = db.Column(db.String(100))
    phone_number = db.Column(db.String(20))
    coordinates = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Establish a relationship with PlaceGallery using back_populates to avoid naming conflicts
    galleries = relationship('PlaceGallery', back_populates='place', lazy=True)


    # Relationship with OpeningHours
    opening_hours = relationship('OpeningHours', back_populates='place', lazy=True)

class OpeningHours(db.Model):
    __tablename__ = 'opening_hours'
    id = db.Column(db.Integer, primary_key=True)
    day_of_week = db.Column(db.String(10))  # e.g., "Monday", "Tuesday"
    open_time = db.Column(db.Time)  # Opening time (e.g., 09:00:00)
    close_time = db.Column(db.Time)  # Closing time (e.g., 17:00:00)
    place_id = db.Column(db.Integer, db.ForeignKey('place.id'))

    # Relationship with Place
    place = relationship('Place', back_populates='opening_hours')
    
    
class PlaceGallery(db.Model):
    __tablename__ = 'place_gallery'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300))
    place_id = db.Column(db.Integer, db.ForeignKey('place.id'))

    # Define the inverse relationship using back_populates
    place = relationship('Place', back_populates='galleries')


class Duel(db.Model):
    __tablename__ = 'duel'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    notice = db.Column(db.String(10000))
    date_duel = db.Column(db.DateTime(timezone=True), default=func.now())
    openhour = db.relationship('OpenHour', backref='duel', uselist=False)
    season_id = db.Column(db.Integer, db.ForeignKey('season.id', ondelete="CASCADE"))
    round_id = db.Column(db.Integer, db.ForeignKey('round.id', ondelete="CASCADE"))
    groupz_id = db.Column(db.Integer, db.ForeignKey('groupz.id'))

class Sport(db.Model):
    __tablename__ = 'sport'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)

class OpenHour(db.Model):
    __tablename__ = 'openhour'
    id = db.Column(db.Integer, primary_key=True)
    notice = db.Column(db.String(500))
    oh_from = db.Column(db.DateTime(timezone=True), default=func.now())
    oh_to = db.Column(db.DateTime(timezone=True), default=func.now())
    duel_id = db.Column(db.Integer, db.ForeignKey('duel.id'))



class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    stripe_link = db.Column(db.String(100), nullable=False)
    youtube_link = db.Column(db.String(300), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=func.now())
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_visible = db.Column(db.Boolean(), default=True)
    price = db.Column(db.DECIMAL(precision=10, scale=2), nullable=False)
    old_price = db.Column(db.DECIMAL(precision=10, scale=2), nullable=False)
    product_category_id = db.Column(db.Integer, db.ForeignKey('product_category.id'), nullable=False)
    product_gallery = db.relationship('ProductGallery', backref='gallpr', lazy=True)

    def __repr__(self):
        return f"Product('{self.title}', '{self.date_posted}', '{self.product_category_id}')"

class ProductCategory(db.Model):
    __tablename__ = 'product_category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)

class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)

class ProductGallery(db.Model):
    __tablename__ = 'product_gallery'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    image_file2 = db.Column(db.String(30), nullable=False)
    orderz = db.Column(db.Integer)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

class Order(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    produc_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer)
    amount = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_paid = db.Column(db.Boolean(), default=False)
    order_date = db.Column(db.DateTime, nullable=False, default=func.now())
    storno = db.Column(db.Boolean(), default=False)
    stripe_subscription_id = db.Column(db.String(255), unique=False, nullable=True)

class PaymentCard(db.Model):
    __tablename__ = 'payment_cards'
    id = db.Column(db.Integer, primary_key=True)
    card_number = db.Column(db.String(16), nullable=False)
    expiration_date = db.Column(db.Date, nullable=False)
    cvc = db.Column(db.String(3), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, card_number, expiration_date, cvc, user_id):
        self.card_number = card_number
        self.expiration_date = expiration_date
        self.cvc = cvc
        self.user_id = user_id

class PaymentMethod(db.Model):
    __tablename__ = 'payment_method'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    card_token = db.Column(db.String(255), nullable=False)

class PushSubscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    endpoint = db.Column(db.String, nullable=False)
    p256dh = db.Column(db.String, nullable=False)
    auth = db.Column(db.String, nullable=False)

    user = db.relationship('User', backref='push_subscriptions')










user_datastore = SQLAlchemyUserDatastore(db, User, Role)

# Additional helper functions and configurations related to user and security can go here
