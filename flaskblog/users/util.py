import os
import secrets

from flask import url_for, current_app
from flask_mail import Message

from flaskblog import mail



def save_picture(form_picture):
    if form_picture:
        random_hex = secrets.token_hex(8)
        _, f_ext = os.path.splitext(form_picture.filename)
        picture_fn = random_hex + f_ext
        picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)
        size = (625, 625)
        form_picture.save(picture_path)

        return picture_fn


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f"""To reset your password, click the following link:
{url_for('users.reset_token', token=token, _external=True)}
If you did not make this request, then please ignore this email and no changes will be made.    
"""
    mail.send(msg)
