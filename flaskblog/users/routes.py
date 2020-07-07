import re
from operator import itemgetter

import requests
from flask import render_template, redirect, url_for, flash, request, Blueprint
from flask_login import login_user, logout_user, login_required, user_loaded_from_cookie

from flaskblog import db, bcrypt, login_manager, jsonify
from flaskblog.models import Post, Business, Admin, AdminSchema, Images, Videos
from flaskblog.users.decorator import check_confirmed
from flaskblog.users.email import send_email
from flaskblog.users.forms import *
from flaskblog.users.token import generate_confirmation_token, confirm_token
from flaskblog.users.util import save_picture, send_reset_email

email_regex = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
name_regex = re.compile(r'^[a-zA-Z]+$')
password_regex = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])")

users = Blueprint('users', __name__)

login_manager.session_protection = None


# ^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[a-z])


@users.route('/confirm/<token>')
@login_required
def confirm_email(token):
    try:
        email = confirm_token(token)
    except:
        flash('The confirmation link is invalid or has expired.', 'danger')
    user = User.query.filter_by(email=email).first_or_404()
    if user.confirmed:
        flash('Account already confirmed. Please login.', 'success')
    else:
        user.confirmed = True
        db.session.add(user)
        db.session.commit()
        flash('Your account has been confirmed. Thanks!', 'success')
    return redirect(url_for('main.home'))


@users.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if request.method == 'POST':

        if request.form['password'] != request.form['confirm_password']:
            flash("Passwords does not match!. Try again", 'danger')
            return redirect(url_for('users.register'))

        if not email_regex.match(request.form['email']):
            flash("Invalid Email Address!", 'danger')
            return redirect(url_for('users.register'))
        if not password_regex.match(request.form['password']):
            flash(
                "password must contain at least one smallcase letter!, password must contain at least one Capital case letter !, password must contain at least one digit!, password must not be less than 8 characters!",
                'danger')

            return redirect(url_for('users.register'))

        user = User.query.filter_by(email=request.form.get('email')).first()
        if user:
            flash('This email is already taken by another user, Please try another one.', 'danger')
            return redirect(url_for('users.register'))
        user = User.query.filter_by(username=request.form.get('username')).first()
        if user:
            flash('This username is already taken by another user, Please try another one.', 'danger')
            return redirect(url_for('users.register'))

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, confirmed=True)
        db.session.add(user)
        db.session.commit()
        token = generate_confirmation_token(user.email)
        confirm_url = url_for('users.confirm_email', token=token, _external=True)
        html = render_template('confirm_url.html', confirm_url=confirm_url)
        subject = "Please confirm your email"
        send_email(user.email, subject, html)

        login_user(user)

        flash('A confirmation email has been sent via email.', 'success')
        # flash('Your account has been created! Log in', 'success')

        return redirect(url_for("users.unconfirmed"))

    return render_template('register.html', title='Register', form=form)


@users.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login failed. please check email and password', 'danger')
    return render_template('login.html', title="Login", form=form)


@users.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@users.route('/posts')
@login_required
@check_confirmed
def posts():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(author=current_user) \
        .order_by(Post.date_posted.desc()) \
        .paginate(page=page, per_page=20)

    return render_template('posts.html', posts=posts, title='My posts')

@users.route('/posts/images')
@login_required
@check_confirmed
def image_posts():
    page = request.args.get('page', 1, type=int)
    posts = Images.query.filter_by(imgs=current_user) \
        .order_by(Images.date_posted.desc()) \
        .paginate(page=page, per_page=20)

    return render_template('media_post.html', posts=posts, title='My posts')

@users.route('/posts/videos')
@login_required
@check_confirmed
def videos_posts():
    page = request.args.get('page', 1, type=int)
    posts = Videos.query.filter_by(vids=current_user) \
        .order_by(Videos.date_posted.desc()) \
        .paginate(page=page, per_page=20)

    return render_template('media_video.html', posts=posts, title='My posts')


@users.route("/account", methods=['GET', 'POST'])
@login_required
@check_confirmed
def account():
    form = UpdateAccountForm()
    user = User.query.filter_by(email=request.form.get('email')).first()
    if user and user != current_user:
        flash('This email is already used by another user', 'danger')
        return redirect(url_for('users.account'))
    user = User.query.filter_by(username=request.form.get('username')).first()
    if user and user != current_user:
        flash('This username is already used by another user', 'danger')
        return redirect(url_for('users.account'))

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
        flash('Your account has been updated!', 'success')
        return redirect(url_for('users.account'))

    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        current_user.confirmed = True
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(author=current_user) \
        .order_by(Post.date_posted.desc()) \
        .paginate(page=page, per_page=10)

    cont = Business.query.filter_by(therapy=current_user).first()


    return render_template('account.html', title='Account',
                           image_file=image_file, form=form, posts=posts, cont=cont)


@users.route('/users/<string:username>')
@check_confirmed
@login_required
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


    return render_template('user_posts.html', poss=poss,ptss=ptss, posts=posts, pots=pots,user=user, posk=posk)


@users.route('/users/images/<string:username>')
@check_confirmed
@login_required
def user_imgs(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Images.query.filter_by(imgs=user) \
        .order_by(Images.date_posted.desc()) \
        .paginate(page=page, per_page=20)
    pots = Images.query.filter_by(imgs=current_user) \
        .order_by(Images.date_posted.desc()) \
        .paginate()
    posk = Images.query \
        .order_by(Images.date_posted.desc()) \
        .paginate()


    return render_template('user_imgs.html', posts=posts, pots=pots,user=user, posk=posk)
@users.route('/users/videos/<string:username>')
@check_confirmed
@login_required
def user_vids(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Videos.query.filter_by(vids=user) \
        .order_by(Videos.date_posted.desc()) \
        .paginate(page=page, per_page=20)
    pots = Videos.query.filter_by(vids=current_user) \
        .order_by(Videos.date_posted.desc()) \
        .paginate()
    posk = Videos.query \
        .order_by(Videos.date_posted.desc()) \
        .paginate()


    return render_template('user_vids.html', posts=posts, pots=pots,user=user, posk=posk)

@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', title='Reset Password', form=form)


@users.route('/setting', methods=['GET', 'POST'])
@check_confirmed
@login_required
def setting():
    form= ReportProblemForm()
    cont = Business.query.filter_by(therapy=current_user).first()
    if form.validate_on_submit():
        report_problem= form.report_problem.data
        report= Admin(report_a_problem=report_problem, adm=current_user)
        db.session.add(report)
        db.session.commit()
    return render_template('setting.html', title='Settings', cont=cont, form=form)


@users.route('/unconfirmed')
@login_required
def unconfirmed():
    if current_user.confirmed:
        return redirect(url_for('main.home'))
    return render_template('unconfirmed.html', title='Unconfirmed')


@users.route('/resend')
@login_required
def resend_confirmation():
    token = generate_confirmation_token(current_user.email)
    confirm_url = url_for('users.confirm_email', token=token, _external=True)
    html = render_template('confirm_url.html', confirm_url=confirm_url)
    subject = "Please confirm your email"
    send_email(current_user.email, subject, html)
    flash('A new confirmation email has been sent.', 'success')
    return redirect(url_for('users.unconfirmed'))


@users.route('/users/<int:id>/<int:user_id>', methods=['GET', 'POST'])
def delete_user(id, user_id):
    user = User.query.get_or_404(id)
    post = Post.query.get_or_404(user_id)

    db.session.delete(user)
    db.session.delete(post)
    db.session.commit()
    return '', 204

