from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from flaskblog import db
from flaskblog.groups.forms import TopicForm
from flaskblog.main.form import PhotoForm, SharePostForm, VideoForm
from flaskblog.main.utils import save_img as svimg
from flaskblog.models import Business, Groups, Images, Post, PostSchema, Room, Topic, User, UserSchema, Videos
from flaskblog.posts.forms import PostForm
from flaskblog.posts.utils import save_img
from flaskblog.users.decorator import check_confirmed

main = Blueprint('main', __name__)

@main.route('/api/posts')
def posts():
    posts = Post.query.order_by(Post.date_posted.desc()).all()
    post_schema = PostSchema(many=True)
    res = post_schema.dump(posts)
    return jsonify(res)

@main.route('/api/post', methods=['POST'])
@login_required
@check_confirmed
def create_post():
    content = request.json.get('content')
    public_id = str(shortuuid.uuid())
    post = Post(content=content, author=current_user, public_id=public_id)
    db.session.add(post)
    db.session.commit()
    return jsonify({'message': 'Post created!'}), 201

@main.route('/api/images', methods=['POST'])
@login_required
def upload_image():
    photo_file = save_img(request.json.get('photo'))
    public_id = str(shortuuid.uuid())
    image = Images(photo_filename=photo_file, photo_data=request.json.get('photo').read(), imgs=current_user, plic_id=public_id)
    db.session.add(image)
    db.session.commit()
    return jsonify({'message': 'Image uploaded!'}), 201

@main.route('/api/videos', methods=['POST'])
@login_required
def upload_video():
    pic_file = svimg(request.json.get('video'))
    public_id = str(shortuuid.uuid())
    video = Videos(img_filename=pic_file, img_data=request.json.get('video').read(), vids=current_user, publ_id=public_id)
    db.session.add(video)
    db.session.commit()
    return jsonify({'message': 'Video uploaded!'}), 201

@main.route('/api/topics', methods=['POST'])
@login_required
def create_topic():
    name = request.json.get('name')
    public_id = str(shortuuid.uuid())
    topic = Topic(name=name, creator=current_user, pub_id=public_id)
    db.session.add(topic)
    db.session.commit()
    return jsonify({'message': 'Topic created!'}), 201
