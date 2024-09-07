import os
import secrets
# from PIL import Image
from flask import url_for, current_app
from flask_mail import Message

from website import mail, celery


@celery.task
def send_new_round_email(user,what,season):
    msg = Message('Your '+ what,
                  sender=('LeagMe.com', 'info@dartsclub.sk'),
                  recipients=[user])
    msg.html = f'''<center><h1>YOUR NEW ROUND STARTED</h1>
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
        href="{url_for('views.home', season=season, _external=True)}">LET'S SEE</a>
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




# def send_reset_email(user):
#     token = user.get_reset_token()
#     msg = Message('Password Reset Request',
#                   sender=('DARTS CLUB','info@dartsclub.sk'),
#                   recipients=[user.email])
#     msg.body = f'''To reset your password, visit the following link:
# {url_for('auth.reset_token', token=token, _external=True)}
# If you did not make this request then simply ignore this email and no changes will be made.
# '''
#     mail.send(msg)


# def send_confirm_email(user):
#     token = user.get_confirm_token()
#     msg = Message('Confirm your register email',
#                   sender=('DARTS CLUB','info@dartsclub.sk'),
#                   recipients=[user.email])
#     msg.body = f'''To confirm your email, click on the following link:
# {url_for('auth.confirm_token', token=token, _external=True)}
# If you did not make this request then simply ignore this email.
# '''
#     mail.send(msg)



# def environment():
#     """
#     This is not how you want to handle environments in a real project,
#     but for the sake of simplicity I'll create this function.

#     Look at using environment variables or dotfiles for these.
#     """
#     return {
#         "billing": {
#             "stripe": {
#                 "token": "****",
#                 "product": "****",
#             }
#         }

#     }
    
    