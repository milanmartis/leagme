from flask import Blueprint, render_template, request, flash, redirect, url_for, session, current_app, jsonify
from .models import User, Season, PaymentCard, Product, Order, PaymentMethod, Role
from . import db, bcrypt
from flask_login import login_user, login_required, logout_user, current_user
from flask_security.utils import login_user  # Importujte správne login_user z Flask-Security-too

from flask_security import current_user, Security, SQLAlchemyUserDatastore, roles_accepted
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError, DataRequired, Email, EqualTo, StopValidation
from werkzeug.security import generate_password_hash, check_password_hash
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.consumer import oauth_authorized
from flask_mail import Message
from website import mail
from sqlalchemy.exc import IntegrityError
import stripe
import boto3
import random
import os
from datetime import datetime
from dotenv import load_dotenv
print("Stav používateľa po prihlásení:", current_user)
print("****************************qqq**********************")
# Načítanie environmentálnych premenných
load_dotenv()
from flask_security.utils import hash_password, verify_and_update_password
from functools import wraps
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
                flash("You do not have permission to access this page.", "danger")
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
    if request.method == 'POST' and request.form.get('email'):
        email = request.form.get('email')
        password = request.form.get('password')

        stmt = db.select(User).where(User.email == email)
        user = db.session.scalar(stmt)

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





@auth.route('/login/google')
def google_login():
    # if not google.authorized:
    #     return redirect(url_for('google.login'))

    resp = google.get("/oauth2/v2/userinfo")
    if not resp.ok:
        flash("Failed to fetch user info from Google.", "error")
        return redirect(url_for('security.login'))

    user_info = resp.json()
    email = user_info["email"]

    user = User.query.filter_by(email=email).first()
    if user:
        user.last_login_at = user.current_login_at
        user.current_login_at = datetime.utcnow()
        user.last_login_ip = user.current_login_ip
        user.current_login_ip = request.remote_addr
        user.login_count += 1
        db.session.commit()
        login_user(user)
        flash("Logged in successfully with Google!", "success")
        return redirect(url_for('home'))

    new_user = User(email=email, first_name=user_info["name"])
    db.session.add(new_user)
    db.session.commit()
    login_user(new_user)
    flash("Account created and logged in successfully with Google!", "success")
    return redirect(url_for('home'))





@auth.route('/logout')
@login_required
def logout():
    logout_user()
    session["name"] = None
    session['logged_in'] = False
    return redirect(url_for('auth.login'))




@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email', None)
        first_name = request.form.get('first_name', None)
        password1 = request.form.get('password1', None)
        password2 = request.form.get('password2', None)

        user = User.query.filter_by(email=email).first()
        nickname = User.query.filter(User.first_name.ilike(first_name)).first()

        if user:
            flash('Email already exists.', category='error')
        elif nickname:
            flash("User name already exists.", category="error")
        elif len(email) < 4:
            flash("Email must be greater than 3 chars", category="error")
        elif len(first_name) < 2:
            flash("First Name must be greater than 1 char", category="error")
        elif password1 != password2:
            flash("Passwords don't match", category="error")
        elif len(password1) < 7:
            flash("Passwords must be at least 7 chars", category="error")
        else:
            hashed_password = bcrypt.generate_password_hash(password1).decode('utf-8')
            new_user = User(email=email, first_name=first_name, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            send_confirm_email(new_user)
            flash("Account created. Check your email to confirm account.", category="success")
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
                  sender=('Darts Club', 'info@dartsclub.sk'),
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
                  sender=('Darts Club', 'info@dartsclub.sk'),
                  recipients=[user.email])
    msg.html = f'''<center><h1>To confirm your email, click on the following link</h1>
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

    
    # return jsonify({'message': 'Karta úspešne pridaná'})
@auth.route('/user/cancel_subscription', methods=['POST'])
def cancel_subscription():
    try:
        # Get the subscription ID from the request
        subscription_id = request.form['subscription_id']
        produc_id = request.form['produc_id']
        subscription = stripe.Subscription.retrieve(subscription_id)
        subscription.delete()
        print(produc_id)
        print('--------------------')
        
        # Default role_to_delete
        role_to_delete = None
        
        if produc_id == '45':
            role_to_delete = 'Player'
        elif produc_id == '46':
            role_to_delete = 'Manager'
        
        if role_to_delete is not None:
            user = User.query.get(current_user.id)
            role = Role.query.filter_by(name=str(role_to_delete)).first()
            if role:
                user.roles.remove(role)
                db.session.commit()

        user = User.query.get(current_user.id)
        user.stripe_subscription_id = ''
        
        # Update orders (assuming this should be a loop or query, not a direct update)
        orders = Order.query.filter(Order.user_id == current_user.id).all()
        for order in orders:
            order.storno = True
        
        db.session.commit()

        # You can also update your database to reflect the canceled subscription
        # For example, mark the subscription as canceled in your database

        flash('Subscription canceled successfully.', category='success')
        return redirect(url_for('auth.user_details'))

    except Exception as e:
        # Handle other errors
        return str(e)


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

        # Vytvorenie Stripe zákazníka
        customer = stripe.Customer.create(
            email=email,
            payment_method=payment_method_id,
            invoice_settings={
                'default_payment_method': payment_method_id,
            },
        )

        # Vytvorenie predplatného
        subscription = stripe.Subscription.create(
            customer=customer.id,
            items=[{'price': amount}],  # Použite price_id, nie konkrétnu sumu
            expand=['latest_invoice.payment_intent']  # Zabezpečí, že payment_intent bude dostupný
        )

        payment_intent = subscription.latest_invoice.payment_intent

        if payment_intent.status == 'requires_action':
            # Platba vyžaduje 3D Secure overenie
            return jsonify({
                'requires_action': True,
                'payment_intent_client_secret': payment_intent.client_secret,
                'subscription_id': subscription.id,
                'product_id': product_id,
                'role_name': role_name
            })

        if payment_intent.status == 'succeeded':
            # Platba bola úspešná bez potreby 3D Secure overenia
            save_order_to_database(user_id, product_id, subscription.id, role_name)
            flash("Thanks for your purchase.", category="success")
            return jsonify({'subscription_id': subscription.id})

    except stripe.error.CardError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400


def save_order_to_database(user_id, product_id, subscription_id, role_name):
    # Vytvorenie novej objednávky
    new_order = Order(produc_id=product_id, quantity=1, amount=1, user_id=user_id, stripe_subscription_id=subscription_id)
    db.session.add(new_order)

    # Pridanie roly užívateľovi
    user = User.query.get(user_id)
    role = Role.query.filter_by(name=role_name).first()
    if role:
        user.roles.append(role)
        user.stripe_subscription_id = subscription_id
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

        save_order_to_database(user_id, product_id, subscription_id, role_name)
        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@auth.route('/account', methods=['GET', 'POST'])
@login_required
def user_details():

    
    if request.method == 'POST':

        useride = request.form.get('useride')
        # email = request.form.get('email')
        first_name = request.form.get('first_name_update')

        password_old = request.form.get('password_old')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        user = User.query.get(useride)
        nickname = User.query.filter(User.first_name.like(first_name)).filter(User.first_name.notlike(current_user.first_name)).first()

        print(current_user.first_name)
        if user == '':
           flash('This user doesn\'t exist.', category='error')
        elif len(first_name) < 2:
            flash("First Name must be greater than 1 chars", category="error")
        elif nickname:
            flash("User name already exist.", category="error")
        else:
            if password1 !='':
                if not bcrypt.check_password_hash(user.password, password_old):
                    flash('Old password is not correct!', category='error')
                elif password1 != password2:
                    flash("New passwords don\'t match", category="error")
                elif password_old == password2:
                    flash("New password must be different", category="error")
                elif len(password1) < 7:
                    flash("New passwords must be at least 7 chars", category="error")
                else:
                    user.password = bcrypt.generate_password_hash(password1).decode('utf-8')
                    user.first_name = first_name
                    session["user_name"] = first_name

                    db.session.commit()
                    login_user(user, remember=True)

                    flash("Account updated!", category="success")
                    return redirect(url_for('auth.user_details'))
            else:
                user.first_name = first_name
                session["user_name"] = first_name
                db.session.commit()
                login_user(user, remember=True)

                flash("Account updated!", category="success")
                return redirect(url_for('auth.user_details'))

    # user_email = session.get('user_email')
    # user_id = session.get('user_id')
    # user_name = session.get('user_name')

    # dict_log = {
    #     'id': user_id, 
    #     'first_name': user_name, 
    #     'email': user_email,
    # }
    cards = PaymentCard.query.filter(PaymentCard.user_id==current_user.id).all()
   
    # order = Order.query.filter(Order.user_id == current_user.id).all()
    
    
    # order = Order.query.with_entities(
    #     Order.stripe_subscription_id,
    #     # Add other columns you need here
    # ).filter(Order.user_id == current_user.id).group_by(Order.stripe_subscription_id).all()
        
        
    orderz = db.session.query(Order.stripe_subscription_id).filter(Order.user_id == current_user.id).group_by(Order.stripe_subscription_id).first()

    # saved_cards = []
    # for order in orderz:
    #     stripe_subscription_id = order[0]
    #     if stripe_subscription_id is not None:
    #         customer = stripe.Customer.retrieve(str(stripe_subscription_id))
    #         saved_cards.append(customer)
    #     else:
    #         saved_cards.append('')
    
    products = Product.query.filter(Product.is_visible==True).order_by(Product.id.asc()).all()
    orders = Order.query.filter(Order.user_id==current_user.id).filter(Order.stripe_subscription_id==current_user.stripe_subscription_id).all()
    #  customer=saved_cards,

    return render_template("users/account.html", checkout_public_key=os.environ.get("STRIPE_PUBLIC_KEY"), orders=orders, products=products, user=current_user, cards=cards)



@auth.route('/my-stats', methods=['GET', 'POST'])
@login_required
def user_stats():
        


        return render_template("users/my-stats.html", user=current_user)
