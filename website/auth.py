from flask import Blueprint, render_template, request, flash, redirect, url_for, session, current_app, jsonify, send_file
from .models import User, Season, PaymentCard, Product, Order, PaymentMethod, Role, BillingInfo
from . import db, bcrypt, argon2
from flask_login import login_user, login_required, logout_user, current_user
from flask_security.utils import login_user  # Importujte správne login_user z Flask-Security-too
from argon2.exceptions import VerifyMismatchError

from flask_security import current_user, Security, SQLAlchemyUserDatastore, roles_accepted
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError, DataRequired, Email, EqualTo, StopValidation
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, SelectMultipleField, IntegerField, RadioField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, StopValidation, NumberRange, Optional
from wtforms import DateField, DateTimeField, DateTimeLocalField, Form
from werkzeug.security import generate_password_hash, check_password_hash
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.consumer import oauth_authorized
from flask_mail import Message
from website import mail
from sqlalchemy.exc import IntegrityError
import stripe
import boto3
from flask_argon2 import Argon2
import uuid
import random
import requests
from website import mail
from .utils import send_new_purchase_email

import os
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()
from flask_security.utils import hash_password, verify_and_update_password
from functools import wraps
from io import BytesIO
from argon2 import PasswordHasher
ph = PasswordHasher()
vapid_public_key=os.environ.get("VAPID_PUBLIC_KEY")

def roles_required(*roles):
    """Dekorátor, ktorý kontroluje, či má používateľ aspoň jednu z požadovaných rolí."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                # Ak používateľ nie je prihlásený, presmeruje ho na prihlasovaciu stránku
                flash("You need to be logged in to access this page.", "warning")
                return redirect(url_for('auth.login'))
            
            # Skontroluje, či má používateľ aspoň jednu z požadovaných rolí
            if not any(role.name in roles for role in current_user.roles):
                flash("You don't have permission, make a subscription", "error")
                return redirect(url_for('views.index'))

            # Ak má používateľ povolenie, vykoná funkciu
            return f(*args, **kwargs)
        return decorated_function
    return decorator
# Stripe konfigurácia
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

# Inicializácia Blueprintu
auth = Blueprint('auth', __name__)
# auth = Blueprint('auth', __name__, url_prefix='/auth')  # Ensure unique name and url_prefix

# Definícia Google blueprintu musí byť pred použitím v dekorátore


@auth.route('/login', methods=['GET', 'POST'])
def login():
    # Ak je už používateľ prihlásený, presmerujte ho na hlavnú stránku
    if current_user.is_authenticated:
        return redirect(url_for('views.index'))
    if request.method == 'POST' and request.form.get('email'):
        email = request.form.get('email')
        password = request.form.get('password')

        stmt = db.select(User).where(User.email == email)
        user = db.session.scalar(stmt)

# $argon2id$v=19$m=65536,t=3,p=4$St7hUxOpI5tD94pxVfzzMQ$HTDMk7BqnpgX7PJtDpuWFEmsdtdfk48XnI4ST2cAkZo
# $argon2id$v=19$m=65536,t=3,p=4$fk/pXYsxxlhLaW3tPYew9g$oYmSLjyfNhzvCreWHFZvdCKTgYdsDrlxvaLdO1ukvmA

        if user:
            if not user.confirm:
                flash('Your account is not activated. Please, confirm it by email!', category='error')
                return render_template("users/login.html", user=current_user)
            else:
                if verify_and_update_password(password, user):
                    # Update login data
                    user.last_login_at = user.current_login_at
                    user.current_login_at = datetime.utcnow()
                    user.last_login_ip = user.current_login_ip
                    user.current_login_ip = request.remote_addr
                    user.login_count += 1
                    user.active = True
                    user.authenticated = True  # Set authenticated to True
                    db.session.commit()
                    login_user(user, remember=True)
                    flash('Logged in successfully!', category='success')
                    next_page = request.args.get('next')
                    return redirect(next_page) if next_page else redirect(url_for('views.index'))
                else:
                    flash('Incorrect password.', category='error')
                    return render_template("users/login.html", user=current_user)
        else:
            flash('User does not exist.', category='error')
            return render_template("users/login.html", user=current_user)

    return render_template("users/login.html", user=current_user, segment='login')






@auth.route('/login/google', methods=['GET', 'POST'])
def google_login():
    print("*********************||||||||||||||||||||*********************")
    if not google.authorized:
        return redirect(url_for('google.login'))  # Redirect to Google login if not authorized

    # Fetch user info from Google API
    resp = google.get("/oauth2/v2/userinfo")  # Try the v1 endpoint
    if not resp.ok:
        flash("Failed to fetch user info from Google.", "error")
        print("Error details:", resp.text)  # Print detailed error for debugging
        return redirect(url_for('security.login'))

    user_info = resp.json()
    email = user_info.get("email")
    print(user_info)

    # Check if email is retrieved correctly
    if not email:
        flash("Email not retrieved from Google. Please check your settings.", "error")
        return redirect(url_for('auth.login'))

    # Find or create a user in your local database
    user = User.query.filter_by(email=email).first()
    if user:
        # Update user login information
        user.last_login_at = user.current_login_at
        user.current_login_at = datetime.utcnow()
        user.last_login_ip = user.current_login_ip
        user.current_login_ip = request.remote_addr
        user.login_count += 1
        user.authenticated = True  # Označiť používateľa ako autentifikovaného
        db.session.commit()
        login_user(user)
        flash("Logged in successfully with Google!", "success")
        return redirect(url_for('views.index'))

    # Create a new user if not found
    new_user = User(
        email=email, 
        first_name=user_info.get("email"),
        authenticated=True, 
        confirm=True, 
        active=True, 
        fs_uniquifier=str(uuid.uuid4()) 
    )
    db.session.add(new_user)
    db.session.commit()
    login_user(new_user)
    flash("Account created and logged in successfully with Google!", "success")
    return redirect(url_for('views.index'))




@auth.route('/logout')
@login_required
def logout():
    logout_user()
    session["name"] = None
    session['logged_in'] = False
    return redirect(url_for('views.index'))



@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('views.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        first_name = request.form.get('first_name', '').strip()
        password1 = request.form.get('password1', '').strip()
        password2 = request.form.get('password2', '').strip()

        # Skontrolujte, či sú všetky polia vyplnené
        if not email or not first_name or not password1 or not password2:
            flash('All fields are required.', category='error')
            return render_template("users/sign_up.html", user=current_user)

        # Skontrolujte, či užívateľ alebo prezývka už existujú
        user = User.query.filter_by(email=email).first()
        nickname = User.query.filter(User.first_name.ilike(first_name)).first()

        if user:
            flash('Email already exists.', category='error')
        elif nickname:
            flash("User name already exists.", category="error")
        elif len(email) < 4:
            flash("Email must be greater than 3 characters.", category="error")
        elif len(first_name) < 2:
            flash("First Name must be greater than 1 character.", category="error")
        elif password1 != password2:
            flash("Passwords don't match.", category="error")
        elif len(password1) < 7:
            flash("Password must be at least 7 characters long.", category="error")
        else:
            # Vygenerujte jedinečný identifikátor fs_uniquifier pomocou UUID
            fs_uniquifier = str(uuid.uuid4())

            # Použite Argon2 na hashovanie hesla
            hashed_password = hash_password(password1)
            new_user = User(email=email, first_name=first_name, password=hashed_password, fs_uniquifier=fs_uniquifier)

            db.session.add(new_user)
            db.session.commit()

            # Pošlite potvrdzovací e-mail novému používateľovi
            send_confirm_email(new_user)
            flash("Account created. Check your email to confirm your account.", category="success")
            return redirect(url_for('auth.login'))

    return render_template("users/sign_up.html", user=current_user)





class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={"placeholder": "Email"})
    submit = SubmitField('Reset password')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first_or_404()
        if user is None:
            raise ValidationError(
                'There is no account with that email. Try another one.')
            


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password',
                             validators=[DataRequired()], render_kw={"placeholder": "Password"}, default = "")
    confirm_password = PasswordField('Confirm password',
                                     validators=[DataRequired(), EqualTo('password')], render_kw={"placeholder": "Confirm password"}, default = "")

    submit = SubmitField('Save new password')



@auth.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('views.index'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_reset_email(user)
            flash('An email has been sent to reset your password.', category="success")
            return redirect(url_for('auth.login'))
        else:
            flash('This email does not exist. Try another one.', category="error")
            return redirect(url_for('auth.reset_request'))

    return render_template('users/reset_request.html', title='Reset Password', form=form, user=current_user)


@auth.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('views.index'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('The used token has expired.', category="error")
        return redirect(url_for('auth.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        # Use hash_password to hash the new password with Argon2
        user.password = hash_password(form.password.data)
        db.session.commit()
        flash('Your password has been changed! You can log in.', category="success")
        return redirect(url_for('auth.login'))
    return render_template('users/reset_token.html', title='Reset Password', form=form)



# @users.route("/confirm_email", methods=['GET', 'POST'])
# def confirm_request():
#     if current_user.is_authenticated:
#         return redirect(url_for('main.home'))
#     form = RequestResetForm()
#     if form.validate_on_submit():
#         user = User.query.filter_by(email=form.email.data).first()
#         send_reset_email(user)
#         flash('An email has been sent with instructions to reset your password.', 'info')
#         return redirect(url_for('users.login'))
#     return render_template('users/reset_request.html', title='Reset Password', form=form, teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table())


@auth.route("/confirm_email/<token>", methods=['GET', 'POST'])
def confirm_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('views.index'))
    user = User.verify_confirm_token(token)
    if user is None:
        flash('The used token has expired.', category="error")
        return redirect(url_for('auth.register'))
    else:
        user.confirm = True

        db.session.commit()
        flash('Your email has been successfully verified! Welcome to the club. You can login.', category="success")
        return redirect(url_for('auth.login'))
    # return render_template('users/confirm_email.html', title='Confirm Register Email', form=form, teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table())



def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender=('LeagMe.com', 'info@dartsclub.sk'),
                  recipients=[user.email])
    msg.html = f'''<center><h1>To reset your password, click on the following button</h1>
<br>
<br>
<a style="
    border-radius: 14px !important;
    background-color: #00EE00;
    border: 2px solid #00EE00;
    color: #030303;
    font-weight: 610;
    font-size: 120%;
    text-decoration:none;
    cursor:pointer;
    padding: 8px 12px 8px 12px;
    margin: 12px;
    width:300px;
    font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;" 
    href="{current_app.url_for('auth.reset_token', token=token, _external=True)}">RESET PASSWORD</a>
<br>
<br>
<p>If you did not make this request then simply ignore this email and no changes will be made.</p>
<br>
<br>
  <source srcset="{ current_app.url_for('static', filename='img/logo-dark.png', _external=True) }" media="(prefers-color-scheme: dark)">
  <img width="120" src="{ current_app.url_for('static', filename='img/logo-light.png', _external=True) }">
<h5>©4NOLIMIT. POWERED BY APPDESIGN.SK</h5>
</center>
'''
    mail.send(msg)


def send_confirm_email(user):
    token = user.get_confirm_token()
    msg = Message('Confirm your register email',
                  sender=('LeagMe.com', 'info@dartsclub.sk'),
                  recipients=[user.email])
    msg.html = f'''<center><h1>To confirm your account, click on the following link</h1>
<br>
<br>
<a style="
    border-radius: 14px !important;
    background-color: #00EE00;
    border: 2px solid #00EE00;
    color: #030303;
    font-weight: 610;
    font-size: 120%;
    text-decoration:none;
    cursor:pointer;
    padding: 8px 12px 8px 12px;
    margin: 12px;
    width:300px;
    font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;" 
    href="{url_for('auth.confirm_token', token=token, _external=True)}">CONFIRM ACCOUNT</a>
<br>
<br>
<p>If you did not make this request then simply ignore this email and no changes will be made.</p>
<br>
<br>
  <source srcset="{ current_app.url_for('static', filename='img/logo-dark.png', _external=True) }" media="(prefers-color-scheme: dark)">
  <img width="120" src="{ current_app.url_for('static', filename='img/logo-light.png', _external=True) }">
<h5>©4NOLIMIT. POWERED BY APPDESIGN.SK</h5>
</center>
'''
    mail.send(msg)



    
    
def environment():
    """
    This is not how you want to handle environments in a real project,
    but for the sake of simplicity I'll create this function.

    Look at using environment variables or dotfiles for these.
    """
    return {
        "billing": {
            "stripe": {
                "token": "****",
                "product": "****",
            }
        }

    }




    # role = Role.query.get_or_404(role_id).first_or_404()











@auth.route('/user/add_card', methods=['POST'])
@login_required
def add_card():
    # card_data = request.json
    # card_number = card_data.get('cardNumber')
    # expiration_date = card_data.get('expirationDate')
    # # cvc = card_data.get('cvc')

    # try:
    #     new_card = PaymentCard(card_number=card_number, expiration_date=expiration_date,cvc='ss', user_id=current_user.id)
    #     db.session.add(new_card)
    #     db.session.commit()
    #     return "Karta úspešne pridaná"
    # except IntegrityError as e:
    #     db.session.rollback()
    #     return "Chyba pri pridaní karty: Duplicity čísla karty", 400
    return jsonify({'message': 'Karta úspešne pridaná'})


@auth.route('/user/add_order/<int:user_id>/<int:product_id>', methods=['POST','GET'])
@login_required
def add_order(user_id,product_id):
    
    product = Product.query.filter(Product.id==product_id).first()

    try:
        new_order = Order(produc_id=product_id, quantity=1, amount=product.price, user_id=user_id)
        db.session.add(new_order)
        db.session.commit()
        flash('Thanks for your purchase.', category='success')
        return redirect(url_for('auth.user_details'))

    except IntegrityError as e:
        db.session.rollback()
        flash('The purchase was interrupted.', category='error')
        return redirect(url_for('auth.user_details'))

    
@auth.route('/user/cancel_subscription', methods=['POST'])
@login_required
def cancel_subscription():
    try:
        # Get the customer ID from the request
        customer_id = request.form.get('subscription_id')
        product_id = request.form.get('product_id')

        # Ensure the customer ID is provided
        if not customer_id:
            flash('Customer ID is missing.', category='error')
            return redirect(url_for('auth.user_details'))
        
        # List subscriptions for the customer
        subscriptions = stripe.Subscription.list(customer=customer_id, limit=1)

        if not subscriptions.data:
            flash('No subscription found for this customer.', category='error')
            return redirect(url_for('auth.user_details'))

        # Get the first subscription from the list
        subscription = subscriptions.data[0]

        # Cancel the subscription
        canceled_subscription = stripe.Subscription.delete(subscription.id)

        # Determine the role to delete based on the product ID
        role_to_delete = None
        if product_id == 'prod_OrfAsMfcZTCPMF':
            role_to_delete = 'Player'
        elif product_id == 'prod_OrfCVSsy37ZOjH':
            role_to_delete = 'Manager'

        # Remove the role from the user
        if role_to_delete:
            user = User.query.get(current_user.id)
            role = Role.query.filter_by(name=str(role_to_delete)).first()
            if role:
                user.roles.remove(role)
                db.session.commit()

        # Mark all user's orders as canceled
        orders = Order.query.filter(Order.user_id == current_user.id).all()
        for order in orders:
            order.storno = True
        
        db.session.commit()

        flash('Subscription canceled successfully.', category='success')
        return redirect(url_for('auth.user_details'))

    except Exception as e:
        # Handle errors
        flash(f'Error cancelling subscription: {str(e)}', category='error')
        return redirect(url_for('auth.user_details'))




@auth.route('/handle_payment_error', methods=['POST'])
def handle_payment_error():
    try:
        data = request.json
        error_message = data.get('error_message')

        # Flash the error message
        flash(f'Payment failed: {error_message}', 'error')
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error handling payment error: {e}")
        return jsonify({'success': False, 'error': str(e)})



@auth.route('/user/make_order', methods=['POST'])
@login_required
def make_order():
    try:
        data = request.json
        email = data['email']
        payment_method_id = data['payment_method_id']
        user_id = data['user_id']
        product_id = data['product_id']
        amount = data['amount']  # Toto by mal byť price_id, ak používate Stripe pre predplatné
        role_name = data['role_name']
      
        customer_id = current_user.stripe_subscription_id  # Retrieve the customer's Stripe ID from the user
  
        
        if not customer_id:
            # If not, create a new Stripe customer
            customer = stripe.Customer.create(
                email=current_user.email,  # Use the user's email to create the customer
                payment_method=payment_method_id,
                invoice_settings={
                    'default_payment_method': payment_method_id,
                },
            )

            # Store the newly created customer ID in the user's profile
            current_user.stripe_subscription_id = customer.id
            db.session.commit()  # Save the user profile with the new Stripe customer ID

        else:
            # If a customer ID already exists, retrieve the customer from Stripe
            customer = stripe.Customer.retrieve(customer_id)

        # Create the subscription for the retrieved or newly created customer
        subscription = stripe.Subscription.create(
            customer=customer.id,
            items=[{'price': amount}],  # Use the price ID (not the amount) from your Stripe dashboard
            expand=['latest_invoice.payment_intent']  # Expand the payment intent for further details
        )

        payment_intent = subscription.latest_invoice.payment_intent

        if payment_intent.status == 'requires_action':
            # Platba vyžaduje 3D Secure overenie
            return jsonify({
                'requires_action': True,
                'payment_intent_client_secret': payment_intent.client_secret,
                'subscription_id': customer.id,
                'product_id': product_id,
                'role_name': role_name,
                'customer_id': customer.id
            })

        if payment_intent.status == 'succeeded':
            # Platba bola úspešná bez potreby 3D Secure overenia
            save_order_to_database(user_id, product_id, subscription.id, role_name, customer.id)
            send_new_purchase_email(current_user.email, role_name)

            flash("Thanks for your purchase.", category="success")
            return jsonify({'subscription_id': subscription.id})

    except stripe.error.CardError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400


def save_order_to_database(user_id, product_id, subscription_id, role_name, customer_id):
    # Vytvorenie novej objednávky
    new_order = Order(produc_id=product_id, quantity=1, amount=1, user_id=user_id, stripe_subscription_id=customer_id)
    db.session.add(new_order)

    # Pridanie roly užívateľovi
    user = User.query.get(user_id)
    role = Role.query.filter_by(name=role_name).first()
    if role:
        user.roles.append(role)
        user.stripe_subscription_id = customer_id
    db.session.commit()


@auth.route('/user/save_order', methods=['POST'])
@login_required
def save_order():
    try:
        data = request.json
        user_id = data['user_id']
        product_id = data['product_id']
        subscription_id = data['subscription_id']
        role_name = data['role_name']
        customer_id = data['customer_id']

        save_order_to_database(user_id, product_id, subscription_id, role_name, customer_id)
        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400




@auth.route('/invoices', methods=['GET', 'POST'])
@login_required
@roles_required('Admin', 'Manager', 'Player')
def get_invoices():
    customer_email = current_user.email  # Načíta e-mail aktuálneho používateľa

    try:
        # Vyhľadajte zákazníka podľa e-mailu
        customers = stripe.Customer.list(email=customer_email)

        if len(customers.data) == 0:
            return "Customer not found."

        customer_id = customers.data[0].id  # Predpokladáme, že prvý výsledok je správny zákazník

        # Získajte faktúry pre zákazníka
        invoices = stripe.Invoice.list(customer=customer_id)

        # Debug výstup pre kontrolu načítania faktúr
        print("Invoices loaded:", invoices.data)

        # Vráťte zoznam faktúr
        return render_template('invoices.html', customer_email=customer_email, invoices=invoices.data)

    except Exception as e:
        return f"An error occurred: {str(e)}"

@auth.route('/users/download_invoice/<invoice_id>', methods=['GET'])
@login_required
@roles_required('Admin', 'Manager', 'Player')
def download_invoice(invoice_id):
    try:
        # Získajte faktúru podľa jej ID
        invoice = stripe.Invoice.retrieve(invoice_id)

        # Získajte URL faktúry vo formáte PDF
        pdf_url = invoice.invoice_pdf

        if not pdf_url:
            return "PDF URL not available for this invoice."

        # Stiahnite PDF faktúru pomocou requests
        response = requests.get(pdf_url)

        if response.status_code == 200:
            # Načítajte PDF do pamäte
            pdf_file = BytesIO(response.content)

            # Pošlite súbor priamo používateľovi bez jeho uloženia na disk
            return send_file(pdf_file, download_name=f'{invoice_id}.pdf', as_attachment=True)

        return "Failed to download invoice PDF."

    except Exception as e:
        return f"An error occurred: {str(e)}"


import re

def validate_vat_number(vat_number, country):
    vat_patterns = {
        "SK": r'^SK\d{10}$',  # Slovensko: SK + 10 číslic
        "DE": r'^DE\d{9}$',   # Nemecko: DE + 9 číslic
        "FR": r'^FR[A-HJ-NP-Z0-9]{2}\d{9}$',  # Francúzsko
        "IT": r'^IT\d{11}$',  # Taliansko: IT + 11 číslic
        # Tu môžete pridať ďalšie krajiny s ich príslušnými vzormi
    }

    pattern = vat_patterns.get(country)
    if pattern:
        return re.match(pattern, vat_number) is not None
    return False  # Ak neexistuje vzor pre danú krajinu, považuje sa za neplatné



# @celery.task
@auth.route('/account', methods=['GET', 'POST'])
@login_required
def user_details():
    form = BillingInfoForm()

    if request.method == 'POST':
        useride = request.form.get('useride')
        first_name = request.form.get('first_name_update')
        phone_number = request.form.get('phone_number_update')
        full_name = request.form.get('full_name_update')
        billing_address = request.form.get('address_update')
        company_name = request.form.get('company_update')
        vat_number = request.form.get('vat_update')
        city = request.form.get('city_update')
        postal_code = request.form.get('postal_code_update')
        country = request.form.get('country_update')

        user = User.query.get(useride)
        
        if not user:
            flash('This user doesn\'t exist.', category='error')
        elif len(first_name) < 2:
            flash("First Name must be greater than 1 chars", category="error")
        else:
            # Aktualizácia údajov o používateľovi
            user.first_name = first_name
            user.phone_number = phone_number
            
            # Aktualizácia údajov o fakturácii
            billing_info = BillingInfo.query.filter_by(customer_id=user.id).first()
            if not billing_info:
                billing_info = BillingInfo(
                    customer_id=user.id,
                    full_name=full_name,
                    billing_address=billing_address,
                    city=city,
                    postal_code=postal_code,
                    country=country,
                    company_name=company_name,
                    vat_number=vat_number
                )
                db.session.add(billing_info)
            else:
                billing_info.full_name = full_name
                billing_info.billing_address = billing_address
                billing_info.city = city
                billing_info.postal_code = postal_code
                billing_info.country = country
                billing_info.company_name = company_name
                billing_info.vat_number = vat_number

            # Overenie DIČ (VAT) čísla, ak je zadané
            if vat_number and not validate_vat_number(vat_number, country):
                flash("Invalid VAT number format for the selected country.", category="error")
                return redirect(url_for('auth.user_details'))

            # Aktualizácia údajov v Stripe, ak má používateľ Stripe Customer ID
            if user.stripe_subscription_id:
                try:
                    stripe.Customer.modify(
                        user.stripe_subscription_id,
                        name=full_name,
                        phone=phone_number,
                        address={
                            "line1": billing_address,
                            "city": city,
                            "postal_code": postal_code,
                            "country": country
                        },
                        # shipping={
                        #     "name": full_name,
                        #     "address": {
                        #         "line1": billing_address,
                        #         "city": city,
                        #         "postal_code": postal_code,
                        #         "country": country
                        #     }
                        # },
                        metadata={
                            "company_name": company_name,  # Pridanie názvu firmy do metadata
                            "vat_number": vat_number
                        },
                        tax_exempt="none",
                        tax_id_data=[{
                            "type": "eu_vat",
                            "value": vat_number,
                        }] if vat_number else []
                    )
                except stripe.error.StripeError as e:
                    flash(f"Error updating Stripe customer: {e.user_message}", category="error")

            db.session.commit()
            login_user(user, remember=True)

            flash("Account updated!", category="success")
            return redirect(url_for('auth.user_details'))

    billing_info = BillingInfo.query.filter_by(customer_id=current_user.id).first()
    cards = PaymentCard.query.filter(PaymentCard.user_id == current_user.id).all()
    products = Product.query.filter(Product.is_visible == True).order_by(Product.id.asc()).all()
    orders = Order.query.filter(Order.user_id == current_user.id).all()

    return render_template(
        "users/account.html", 
        checkout_public_key=os.environ.get("STRIPE_PUBLIC_KEY"), 
        vapid_public_key=vapid_public_key, 
        user=current_user, 
        cards=cards, 
        products=products, 
        orders=orders, 
        billing_info=billing_info, 
        form=form, 
        user_country_code=billing_info.country if billing_info else ''
    )




@auth.route('/delete_payment_method', methods=['POST'])
@login_required
def delete_payment_method():
    data = request.get_json()
    payment_method_id = data.get('payment_method_id')
    try:
        # Odstránenie platobnej metódy zo Stripe
        stripe.PaymentMethod.detach(payment_method_id)
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error deleting payment method: {str(e)}")  # Debugging output
        return jsonify({'success': False, 'error': str(e)}), 500
    
@auth.route('/account/stripe_data', methods=['GET'])
@login_required
def get_stripe_data():
    customer_id = current_user.stripe_subscription_id  # Predpokladám, že máte stripe_customer_id alias stripe_subscription_id uložené v používateľskom objekte
    # print(customer_id)
    if not customer_id:
        print("No Stripe subscription ID found for the user.")
        return jsonify({"error": "No subscription ID found."}), 400
    try:
        # Získanie všetkých faktúr pre zákazníka
        all_invoices = []
        invoices = stripe.Invoice.list(customer=customer_id, limit=100, expand=['data.lines'])

        # Pridanie načítaných faktúr
        all_invoices.extend(invoices.data)

        # Načítanie všetkých strán faktúr (ak je viac než 100)
        while invoices.has_more:
            invoices = stripe.Invoice.list(customer=customer_id, limit=100, starting_after=invoices.data[-1].id, expand=['data.lines'])
            all_invoices.extend(invoices.data)

        # Načítanie platobných metód pre zákazníka
        payment_methods = stripe.PaymentMethod.list(customer=customer_id, type="card")
        all_payment_methods = payment_methods.data

        # Načítanie predplatných pre zákazníka
        subscriptions = stripe.Subscription.list(customer=customer_id)

        # Pripraviť odpoveď so Stripe dátami
        stripe_data = {
            'invoices': [invoice.to_dict() for invoice in all_invoices],
            'payment_methods': [pm.to_dict() for pm in all_payment_methods],
            'subscriptions': [subscription.to_dict() for subscription in subscriptions.data]
        }

        # print(stripe_data)  # Debugging output
        return jsonify(stripe_data)

    except Exception as e:
        print(f"Error fetching data from Stripe: {str(e)}")  # Debugging output
        return jsonify({"error": str(e)}), 500
        

    
@auth.route('/users/add_payment_method', methods=['GET', 'POST'])
@login_required
@roles_required('Admin', 'Manager', 'Player')
def add_payment_method():
    if request.method == 'POST':
        try:
            # Získajte údaje z formulára
            payment_method_id = request.form['payment_method_id']
            customer_email = current_user.email

            # Vyhľadajte zákazníka podľa e-mailu
            customers = stripe.Customer.list(email=customer_email)
            if len(customers.data) == 0:
                return "Customer not found."

            customer_id = customers.data[0].id

            # Pripojte novú platobnú metódu k zákazníkovi
            stripe.PaymentMethod.attach(
                payment_method_id,
                customer=customer_id,
            )

            # Nastavte platobnú metódu ako predvolenú pre fakturáciu
            stripe.Customer.modify(
                customer_id,
                invoice_settings={"default_payment_method": payment_method_id}
            )

            return redirect(url_for('auth.account'))

        except Exception as e:
            return f"An error occurred: {str(e)}"
    return render_template('add_payment_method.html')


@auth.route('/my-stats', methods=['GET', 'POST'])
@login_required
def user_stats():
        


        return render_template("users/my-stats.html", user=current_user)


class BillingInfoForm(FlaskForm):
    billing_address = StringField('Billing Address', validators=[DataRequired(), Length(max=255)])
    city = StringField('City', validators=[DataRequired(), Length(max=100)])
    postal_code = StringField('Postal Code', validators=[DataRequired(), Length(max=20)])
    country = StringField('Country', validators=[DataRequired(), Length(max=100)])
    company_name = StringField('Company Name', validators=[Optional(), Length(max=255)])
    vat_number = StringField('VAT Number', validators=[Optional(), Length(max=50)])
    submit = SubmitField('Submit')