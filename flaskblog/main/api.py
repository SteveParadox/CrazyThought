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

@main.route('/api/home', methods=['GET'])
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=50).items

    post_schema = PostSchema(many=True)
    res = post_schema.dump(posts)

    return jsonify(res)

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

@main_bp.route("/api/post/share/<int:post_id>", methods=['POST'])
@login_required
@check_confirmed
def share_post(post_id):
    post = Post.query.get_or_404(post_id)
    content = request.json.get('content')
    if not content:
        return jsonify({'error': 'Content is required'}), 400
    poss = Post(content=content, author=current_user)
    db.session.add(poss)
    db.session.commit()
    return jsonify({'message': 'Post shared successfully'}), 201

@main.route('/searche', methods=['POST'])
def search():
    data = request.form.get('text')
    results = User.query.filter_by(username=str(data[0]).upper() + data[1:]).all()
    user_schema = UserSchema(many=True)
    res = user_schema.dump(results)
    return jsonify(res)

