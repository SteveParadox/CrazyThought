import re
from operator import itemgetter

import requests
from flask import render_template, redirect, url_for, flash, request, Blueprint, jsonify
from flask_login import login_user, logout_user, login_required, user_loaded_from_cookie

from flaskblog import db, bcrypt, login_manager
from flaskblog.models import Post, Business, Admin, AdminSchema, Images, Videos, UserSchema
from flaskblog.users.decorator import check_confirmed
from flaskblog.users.email import send_email
from flaskblog.users.token import generate_confirmation_token, confirm_token
from flaskblog.users.forms import *
from flaskblog.users.util import save_picture, send_reset_email

email_regex = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
name_regex = re.compile(r'^[a-zA-Z]+$')
password_regex = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])")

users = Blueprint('users', __name__)

login_manager.session_protection = None


@users.route('/confirm/<token>')
@login_required
def confirm_email(token):
    try:
        email = confirm_token(token)
    except:
        return jsonify({'message': 'The confirmation link is invalid or has expired.'}), 400
    user = User.query.filter_by(email=email).first_or_404()
    if user.confirmed:
        return jsonify({'message': 'Account already confirmed. Please login.'}), 400
    else:
        user.confirmed = True
        db.session.add(user)
        db.session.commit()
        return jsonify({'message': 'Your account has been confirmed. Thanks!'}), 200


@users.route("/register", methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    confirm_password = data.get('confirm_password')

    if password != confirm_password:
        return jsonify({'message': 'Passwords do not match!'}), 400
    if not email_regex.match(email):
        return jsonify({'message': 'Invalid Email Address!'}), 400
    if not password_regex.match(password):
        return jsonify({'message': 'Password must contain at least one lowercase letter, one uppercase letter, one digit, and must not be less than 8 characters!'}), 400

    user = User.query.filter_by(email=email).first()
    if user:
        return jsonify({'message': 'This email is already taken by another user. Please try another one.'}), 400
    user = User.query.filter_by(username=username).first()
    if user:
        return jsonify({'message': 'This username is already taken by another user. Please try another one.'}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    user = User(username=username, email=email, password=hashed_password, confirmed=False)
    db.session.add(user)
    db.session.commit()

    token = generate_confirmation_token(user.email)
    confirm_url = url_for('users.confirm_email', token=token, _external=True)
    html = render_template('confirm_url.html', confirm_url=confirm_url)
    subject = "Please confirm your email"
    send_email(user.email, subject, html)

    login_user(user)

    return jsonify({'message': 'A confirmation email has been sent to your email address.'}), 201
  
  
  
  
