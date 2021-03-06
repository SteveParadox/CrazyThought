import time
from operator import itemgetter

import shortuuid
from flask import (Blueprint, jsonify, redirect, render_template, request,
                   url_for)
from flask_login import current_user, login_required
from flaskblog import db, io
from flaskblog.groups.forms import TopicForm
from flaskblog.main.form import PhotoForm, SharePostForm, VideoForm
from flaskblog.main.utils import save_img as svimg
from flaskblog.models import (Business, Groups, Images, Post, PostSchema, Room,
                              Topic, User, UserSchema, Videos)
from flaskblog.posts.forms import PostForm
from flaskblog.posts.utils import save_img
from flaskblog.users.decorator import check_confirmed

main = Blueprint('main', __name__)


@main.route('/')
def loader():
    return render_template('loader.html')


@main.route("/post/share/<int:post_id>", methods=['GET', 'POST'])
@login_required
@check_confirmed
def share_post(post_id):
    post = Post.query.get_or_404(post_id)
    form = SharePostForm()
    das = post.content
    if form.is_submitted():
        poss = Post(content=form.content.data, author=current_user)
        db.session.add(poss)
        db.session.commit()

        return redirect(url_for('main.home', post_id=post.id))
    return render_template('share.html', title='Share Post', form=form,
                           legend='Share Post', post_id=post.id, post=post, das=das)


@main.route('/home/data', methods=['GET', 'POST'])
def data():
    post = Post.query.order_by(Post.content.desc()).all()

    post_schema = PostSchema(many=True)
    res = post_schema.dump(post)

    return jsonify(res)


@main.route('/home', methods=['GET', 'POST'])
def home():
    global pots
    pots = Post.query.filter_by() \
        .order_by(Post.date_posted.desc()) \
        .paginate()
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=50)
    posk = Post.query \
        .order_by(Post.date_posted.desc()) \
        .paginate()
    side = (Groups.query.filter_by().order_by(Groups.comments.desc()).all()[0:5])
    post = Post.query.order_by(Post.content.desc()).all()
    form = PostForm()
    room= ''
    if current_user.is_authenticated:
        room = Room.query.filter_by(host=current_user.username).order_by(Room.created.desc()).all()
    if form.validate_on_submit():
        post = Post(content=form.content.data, author=current_user, public_id=str(shortuuid.uuid()))
        db.session.add(post)
        db.session.commit()

        return redirect(url_for('main.home'))
    form2 = PhotoForm()

    if form2.validate_on_submit():
        file = request.files['photo']
        photo_file = save_img(form2.photo.data)
        post = Images(photo_filename=photo_file, photo_data=file.read(), imgs=current_user,
                      plic_id=str(shortuuid.uuid()))
        db.session.add(post)
        db.session.commit()

        return redirect(url_for('main.home_images'))
    form3 = VideoForm()

    if form3.validate_on_submit():
        file = request.files['video']
        pic_file = svimg(form3.video.data)
        post = Videos(img_filename=pic_file, img_data=file.read(), vids=current_user, publ_id=str(shortuuid.uuid()))
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('main.home_videos'))

    form4 = TopicForm()
    if form4.validate_on_submit():
        topic = Topic(name=form4.name.data, creator=current_user, pub_id=str(shortuuid.uuid()))
        db.session.add(topic)
        db.session.commit()
        return redirect(url_for('groups.topics'))

    if current_user.is_authenticated:
        pots = Post.query.filter_by(author=current_user) \
            .order_by(Post.date_posted.desc()) \
            .paginate()
    return render_template('home.html', posts=posts, form4=form4, pots=pots, form2=form2, form3=form3, posk=posk,
                           side=side, reload=time.time(), form=form, post=post, room=room)


@main.route('/home/images', methods=['GET', 'POST'])
def home_images():
    pots = Images.query.filter_by() \
        .order_by(Images.date_posted.desc()) \
        .paginate()
    page = request.args.get('page', 1, type=int)
    posts = Images.query.filter_by(photo_filename=Images.photo_filename).order_by(Images.date_posted.desc()).paginate(
        page=page, per_page=20)

    posk = Images.query \
        .order_by(Images.date_posted.desc()) \
        .paginate()
    if current_user.is_authenticated:
        pots = Images.query.filter_by(imgs=current_user) \
            .order_by(Images.date_posted.desc()) \
            .paginate()
    return render_template('images.html', posts=posts, reload=time.time(), pots=pots, posk=posk)


@main.route('/home/videos', methods=['GET', 'POST'])
def home_videos():
    pots = Videos.query.filter_by() \
        .order_by(Videos.date_posted.desc()) \
        .paginate()
    page = request.args.get('page', 1, type=int)
    posts = Videos.query.filter_by(img_filename=Videos.img_filename).order_by(Videos.date_posted.desc()).paginate(
        page=page, per_page=20)

    posk = Videos.query \
        .order_by(Videos.date_posted.desc()) \
        .paginate()
    if current_user.is_authenticated:
        pots = Videos.query.filter_by(vids=current_user) \
            .order_by(Videos.date_posted.desc()) \
            .paginate()
    return render_template('videos.html', reload=time.time(), posts=posts, pots=pots, posk=posk)


@main.route('/about', methods=['GET', 'POST'])
def about():
    return render_template('about.html')


@main.route('/tos')
def tos():
    return render_template('tos.html')


@main.route('/cookies')
def cookies():
    return render_template('cookies.html')


@main.route('/search', methods=['GET', 'POST'])
@login_required
@check_confirmed
def searchfile():
    return render_template('searc.html')


@main.route('/searche', methods=['POST'])
def search():
    data = request.form.get('text')
    results = User.query.filter_by(username=str(data[0]).upper() + data[1:]).all()
    user_schema = UserSchema(many=True)
    res = user_schema.dump(results)
    print(res)
    return jsonify(res)


@io.on('thumbs_up')
def ___(data):
    public_id = data['post_id']
    post = Post.query.filter_by(public_id=public_id).first()
    post.love = post.love + 1
    db.session.commit()


@main.route('/like/<int:id>')
def like(id):
    post = Post.query.filter_by(id=id).first()
    post.love = post.love + 1
    db.session.commit()
    return redirect(url_for('main.home'))
