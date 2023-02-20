from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
import random
from flaskblog import db
from flaskblog.models import *
from flaskblog.posts.utils import save_img
from flaskblog.users.decorator import check_confirmed

posts = Blueprint('posts', __name__)

@posts.route("/explore", methods=['GET', 'POST'])
def explore():
    side = (Post.query.order_by(Post.viewed.desc()).all()[0:100])
    return jsonify({'side': side})

@posts.route("/explore/images", methods=['GET', 'POST'])
def trending():
    side = (Images.query.order_by(Images.comments.desc()).all()[0:100])
    x = random.shuffle(side)
    return jsonify({'side': side})

@posts.route("/explore/videos", methods=['GET', 'POST'])
def trending_videos():
    side = (Videos.query.order_by(Videos.comments.desc()).all()[0:100])
    x = random.shuffle(side)
    return jsonify({'side': side})

@posts.route("/tags", methods=['GET', 'POST'])
def tags():
    posts = Post.query.all()
    return jsonify({'posts': [post.to_dict() for post in posts]})

@posts.route("/post/new", methods=['POST'])
@login_required
def new_post():
    data = request.get_json()
    file = data.get('photo')
    pic_file = save_img(file)
    post = Post(content=data.get('content'), author=current_user, img_data=file.read(),
                img_filename=pic_file)
    db.session.add(post)
    db.session.commit()
    return jsonify({'message': 'Post created successfully!'})

@posts.route("/post/<string:public_id>", methods=['POST', 'GET'])
@login_required
@check_confirmed
def post(public_id):
    page = request.args.get('page', 1, type=int)
    post = Post.query.filter_by(public_id=public_id).first()
    post.viewed = post.viewed + 1
    db.session.commit()
    posts = Post.query.order_by(Post.public_id.desc()).all()
    comments = Comment.query.filter_by(post_id=post.id).order_by(Comment.pub_date.desc()).paginate(page=page,
                                                                                                      per_page=20)
    rc = ReplyComment.query.order_by(ReplyComment.pub_date.desc()).all()
    if request.method == 'POST':
        message = request.json.get('message')
        comment = Comment(message=message, post_id=post.id, reply=current)
                          
                         

@posts.route("/post/<string:public_id>/comment/<int:comment_id>", methods=['GET','POST'])
@login_required
@check_confirmed
def reply_comment(public_id, comment_id):
    page = request.args.get('page', 1, type=int)
    post = Post.query.filter_by(public_id=public_id).first()
    comment = Comment.query.filter_by(id=comment_id).first()
    rc = ReplyComment.query.filter_by(comment_id=comment.id).order_by(ReplyComment.pub_date.desc()).paginate(page=page, per_page=20)
    form = ReplyForm()
    if form.validate_on_submit():
        rc = ReplyComment(message=form.message.data, comment=current_user, post_id=post.id, comment_id=comment.id)
        db.session.add(rc)
        comment.replys = comment.replys + 1
        db.session.commit()
        return jsonify({'message': 'Reply added successfully'}), 201
    return jsonify({'message': 'Invalid Request'}), 400

@posts.route("/post/<string:public_id>/update", methods=['PUT'])
@login_required
@check_confirmed
def update_post(public_id):
    post = Post.query.filter_by(public_id=public_id).first()
    if post.author != current_user:
        return jsonify({'message': 'Forbidden'}), 403
    data = request.get_json()
    if not data:
        return jsonify({'message': 'Invalid Request'}), 400
    post.content = data['content']
    post.love = 0
    db.session.commit()
    return jsonify({'message': 'Post updated successfully'}), 200

@posts.route("/post/<int:post_id>/delete", methods=['DELETE'])
@login_required
@check_confirmed
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        return jsonify({'message': 'Forbidden'}), 403
    comment = Comment.query.filter_by(post_id=post_id).all()
    rc = ReplyComment.query.filter_by(post_id=post.id).all()
    for i in rc:
        db.session.delete(i)
    for o in comment:
        db.session.delete(o)
    db.session.delete(post)
    db.session.commit()
    return jsonify({'message': 'Post deleted successfully'}), 200

