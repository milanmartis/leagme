from flask import Blueprint, render_template, request, flash, redirect, url_for, session, app, jsonify
from .models import Product, Note, User, Duel, Season, Groupz, Round, user_duel, user_group, user_season
from . import db, bcrypt
from flask_login import login_user, login_required, logout_user, current_user
from flask_security import roles_required

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
# from flask_bcrypt import Bcrypt
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, SelectMultipleField, IntegerField, RadioField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, StopValidation
auth = Blueprint('auth', __name__)
import datetime
from flask import url_for, current_app
from flask_mail import Message
from website import mail

products = Blueprint('product', __name__)
adminz = [21, 22]




@products.route('/products')
@login_required
@roles_required('Admin')
def index():
    products = Product.query.all()
    return render_template('products/index.html', products=products, user=current_user, adminz=adminz)

@products.route('/products/add', methods=['POST'])
def add():
    title = request.json['title']
    price = request.json['price']
    new_product = Product(title=title, price=price, content='aaa', user_id=1, old_price=1,product_category_id=1)
    db.session.add(new_product)
    db.session.commit()
    return jsonify({'id': new_product.id, 'title': new_product.title, 'price': new_product.price})

@products.route('/products/edit/<int:id>', methods=['PUT'])
def edit(id):
    product = Product.query.get_or_404(id)
    data = request.json
    product.title = data['title']
    product.price = data['price']
    db.session.commit()
    return jsonify({'message': 'Product updated successfully'})

@products.route('/products/delete/<int:id>', methods=['DELETE'])
def delete(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Product deleted successfully'})