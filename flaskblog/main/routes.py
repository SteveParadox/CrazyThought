import time
from operator import itemgetter
import random
import shortuuid
import asyncio
from flask import (Blueprint, jsonify, redirect, render_template, request,
                   url_for)
from flask_login import current_user, login_required
from flaskblog import db, io, cache, graph
from flaskblog.main.form import PhotoForm, SharePostForm, VideoForm, TopicForm
from flaskblog.main.utils import save_img as svimg
from flaskblog.models import (Business, Groups, Images, Post, PostSchema, Room,
                              Topic, User, UserSchema, Videos)
from flaskblog.posts.forms import PostForm
from flaskblog.posts.utils import save_img
from flaskblog.users.decorator import check_confirmed
import string
from py2neo import Graph, Node, Relationship
from flaskblog.tasks import data_task, create_post_task

main = Blueprint('main', __name__)

@main.route('/')
@cache.cached() 
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
    test_task.delay()
    return "Data added to the graph database."

@main.route('/home', methods=['GET', 'POST'])
def home():
    page = request.args.get('page', 1, type=int)
    pots = None
    room= None
    cypher_query = """
    MATCH (user:User)-[:POSTED]->(post:Post)
    RETURN user.user_id AS user_id, user.user_name AS user_name,
    user.img_file AS image_file,
    post.content AS content, 
    post.comments AS comments, post.public_id AS public_id,
    post.love AS love,
    post.date_posted AS date_posted
    ORDER BY post.date_posted DESC
    LIMIT 50
    """
    result = graph.run(cypher_query)

    posts = []

    for record in result:
        posts.append({
            'user_id': record['user_id'],
            'content': record['content'],
            'public_id': record['public_id'],
            'user_name': record['user_name'],
            'image_file': record['image_file'],
            'comments': record['comments'],
            'love': record['love'],
            'date_posted': record['date_posted'].isoformat()[:10],
        })
    posk = Post.query.paginate()
    side = (Groups.query.filter_by().order_by(Groups.comments.desc()).all()[0:5])
    form = PostForm()
    
    if current_user.is_authenticated:
        room = Room.query.filter_by(host=current_user.username)\
        .order_by(Room.created.desc()).all()
    if form.validate_on_submit():
        post = Post(content=form.content.data, author=current_user, public_id=str(shortuuid.uuid()))
        db.session.add(post)
        db.session.commit()
        create_post_task.delay(user_id=current_user.id)
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
        post = Videos(img_filename=pic_file, img_data=file.read(),
         vids=current_user, publ_id=str(shortuuid.uuid()))
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('main.home_videos'))

    if current_user.is_authenticated:
        pots = Post.query.filter_by(author=current_user) \
            .order_by(Post.date_posted.desc())\
            .paginate()
    return render_template('home.html', posts=posts, pots=pots, form2=form2, form3=form3, posk=posk,
                           side=side, reload=time.time(), form=form, post=posts, room=room)


@main.route('/home/images', methods=['GET', 'POST'])
def home_images():
    pots = Images.query.filter_by() \
        .order_by(Images.date_posted.desc()) \
        .paginate()
    page = request.args.get('page', 1, type=int)
    posts = Images.query.filter_by(photo_filename=Images.photo_filename)\
    .order_by(Images.date_posted.desc()).paginate(
        page=page, per_page=20)

    posk = Images.query \
        .order_by(Images.date_posted.desc()) \
        .paginate()
    if current_user.is_authenticated:
        pots = Images.query.filter_by(imgs=current_user) \
            .order_by(Images.date_posted.desc()) \
            .paginate()
    return render_template('images.html', posts=posts, reload=time.time(), 
    pots=pots, posk=posk)


@main.route('/home/videos', methods=['GET', 'POST'])
def home_videos():
    pots = Videos.query.filter_by() \
        .order_by(Videos.date_posted.desc()) \
        .paginate()
    page = request.args.get('page', 1, type=int)
    posts = Videos.query.filter_by(img_filename=Videos.img_filename)\
    .order_by(Videos.date_posted.desc()).paginate(
        page=page, per_page=20)

    posk = Videos.query \
        .order_by(Videos.date_posted.desc()) \
        .paginate()
    if current_user.is_authenticated:
        pots = Videos.query.filter_by(vids=current_user) \
            .order_by(Videos.date_posted.desc()) \
            .paginate()
    return render_template('videos.html', reload=time.time(), 
    posts=posts, pots=pots, posk=posk)


@main.route('/about', methods=['GET', 'POST'])
@cache.cached() 
def about():
    return render_template('about.html')


@main.route('/tos')
def tos():
    return render_template('tos.html')


@main.route('/cookies')
@cache.cached() 
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
    results = User.query.filter(User.username.ilike(f'%{data}%')).all()
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


@main.route('/like_post', methods=['POST'])
def like_post():
    post_id = request.json['post_id']
    print(post_id)
    post = Post.query.filter_by(public_id=post_id).first()
    print(post)
    if post:
        post.love += 1
        db.session.commit()
        create_post_task.delay(user_id=current_user.id)

        return jsonify({'message': 'Post liked successfully.', 'likes': post.love})
    else:
        return jsonify({'error': 'Post not found.'}), 404



@main.route('/testing', methods=['GET', 'POST'])
def dsf():
    cypher_query = """
    MATCH (user:User)-[:POSTED]->(post:Post)
    RETURN user.user_id AS user_id, user.user_name AS user_name,
    user.img_file AS image_file,
    post.content AS content, 
    post.comments AS comments, post.public_id AS public_id,
    post.date_posted AS date_posted
    ORDER BY post.date_posted DESC
    LIMIT 50
    """
    result = graph.run(cypher_query)

    data = []

    for record in result:
        data.append({
            'user_id': record['user_id'],
            'content': record['content'],
            'public_id': record['public_id'],
            'user_name': record['user_name'],
            'image_file': record['image_file'],
            'comments': record['comments'],
            'date_posted': record['date_posted'].isoformat(),  
        })

    return jsonify(data)
