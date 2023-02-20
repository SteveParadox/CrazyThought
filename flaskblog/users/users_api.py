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
  
  
  @users.route('/login', methods=['POST'])
def login():
    if current_user.is_authenticated:
        return jsonify({'message': 'Already logged in.'}), 400

    form = LoginForm(request.form)

    if form.validate():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return jsonify({'message': 'Logged in successfully.'}), 200
        else:
            return jsonify({'message': 'Login failed. please check email and password.'}), 400
    else:
        return jsonify({'message': 'Invalid form data.'}), 400

@users.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully.'}), 200

@users.route('/posts', methods=['GET'])
@login_required
@check_confirmed
def posts():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(author=current_user) \
        .order_by(Post.date_posted.desc()) \
        .paginate(page=page, per_page=20)
    user_schema = UserSchema(many=True)
    res = user_schema.dump(posts.items)
    return jsonify(res)

@users.route('/posts/images', methods=['GET'])
@login_required
@check_confirmed
def image_posts():
    page = request.args.get('page', 1, type=int)
    posts = Images.query.filter_by(imgs=current_user) \
        .order_by(Images.date_posted.desc()) \
        .paginate(page=page, per_page=20)
    user_schema = UserSchema(many=True)
    res = user_schema.dump(posts.items)
    return jsonify(res)

@users.route('/posts/videos', methods=['GET'])
@login_required
@check_confirmed
def videos_posts():
    page = request.args.get('page', 1, type=int)
    posts = Videos.query.filter_by(vids=current_user) \
        .order_by(Videos.date_posted.desc()) \
        .paginate(page=page, per_page=20)
    user_schema = UserSchema(many=True)
    res = user_schema.dump(posts.items)
    return jsonify(res)

@users.route('/api/account', methods=['POST'])
@check_confirmed
def account():
    data = request.json
    form = UpdateAccountForm(**data['form'])
    user = User.query.filter_by(email=form.email.data).first()
    if user and user != current_user:
        return jsonify({'message': 'This email is already used by another user'}), 400
    user = User.query.filter_by(username=form.username.data).first()
    if user and user != current_user:
        return jsonify({'message': 'This username is already used by another user'}), 400

    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        if form.email.data != current_user.email:
            current_user.email = form.email.data
            current_user.confirmed = False
            token = generate_confirmation_token(user.email)
            confirm_url = url_for('users.confirm_email', token=token, _external=True)
            html = render_template('confirm_url.html', confirm_url=confirm_url)
            subject = "Please confirm your email"
            send_email(user.email, subject, html)

            login_user(user)
        db.session.commit()
    if form.email.data == current_user.email:
        return jsonify({'message': 'Your account has been updated!'}), 200

    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        current_user.confirmed = True
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(author=current_user) \
        .order_by(Post.date_posted.desc()) \
        .paginate(page=page, per_page=10)

    user_schema = UserSchema()
    res = user_schema.dump(current_user)
    res['image_file'] = image_file
    res['posts'] = [post.to_dict() for post in posts.items]
    return jsonify(res)


@users.route('/api/users/<string:username>', methods=['GET'])
@check_confirmed
def user_post(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user) \
        .order_by(Post.date_posted.desc()) \
        .paginate(page=page, per_page=20)
    pots = Post.query.filter_by(author=current_user) \
        .order_by(Post.date_posted.desc()) \
        .paginate()
    posk = Post.query \
        .order_by(Post.date_posted.desc()) \
        .paginate()
    poss = Images.query.filter_by(imgs=user).first()
    ptss = Videos.query.filter_by(vids=user).first()

    user_schema = UserSchema()
    res = user_schema.dump(user)
    res['posts'] = [post.to_dict() for post in posts.items]
    res['poss'] = poss.to_dict() if poss else None
    res['ptss'] = ptss.to_dict() if ptss else None
    return jsonify(res)


  
