import os
import secrets
# from PIL import Image
from flask import url_for, current_app
from flask_mail import Message
from app import mail



def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender=('DARTS CLUB','info@dartsclub.sk'),
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('auth.reset_token', token=token, _external=True)}
If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)


def send_confirm_email(user):
    token = user.get_confirm_token()
    msg = Message('Confirm your register email',
                  sender=('DARTS CLUB','info@dartsclub.sk'),
                  recipients=[user.email])
    msg.body = f'''To confirm your email, click on the following link:
{url_for('auth.confirm_token', token=token, _external=True)}
If you did not make this request then simply ignore this email.
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