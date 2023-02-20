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
    return jsonify({
        "posts": [post.to_dict() for post in posts.items],
        "pots": [pot.to_dict() for pot in pots.items],
        "side": [group.to_dict() for group in side],
        "form": form.to_dict(),
        "form2": form2.to_dict(),
        "form3": form3.to_dict(),
        "form4": form4.to_dict(),
        "room": [r.to_dict() for r in room],
    })

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
