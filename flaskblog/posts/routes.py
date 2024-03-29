import random
from flask import render_template, redirect, url_for, flash, request, abort, Blueprint
from flask_login import current_user, login_required
from flaskblog import db, jsonify, cache
from flaskblog.models import *
from flaskblog.posts.forms import PostForm, UpdatePostForm, CommentForm, ReplyForm, CommentsForm
from flaskblog.posts.utils import save_img
from flaskblog.users.decorator import check_confirmed
from sqlalchemy.orm import selectinload
from flaskblog.tasks import delete_post_task


posts = Blueprint('posts', __name__)

@posts.route("/redis", methods=['GET', 'POST'])
def tri():
    tring = trial()
    print(tring)
    return "redis cloud"


@posts.route("/explore", methods=['GET', 'POST'])
@cache.cached() 
def explore():
    side = (Post.query.options(selectinload(Post.author))\
        .order_by(Post.viewed.desc()).all()[0:100])
    return render_template('explore.html', side=side, title='Popular')

@posts.route("/explore/images", methods=['GET', 'POST'])
@cache.cached() 
def trending():
    side = (Images.query.options(selectinload(Images.imgs))\
        .order_by(Images.comments.desc()).all()[0:100])
    x = random.shuffle(side)
    return render_template('trending.html', side=side, title='Popular')

@posts.route("/explore/videos", methods=['GET', 'POST'])
@cache.cached() 
def trending_videos():
    side = (Videos.query.options(selectinload(Videos.vids))\
    .order_by(Videos.comments.desc()).all()[0:100])
    x = random.shuffle(side)
    return render_template('trending_videos.html',
     side=side, title='Popular')


@posts.route("/tags", methods=['GET', 'POST'])
@cache.cached()
def tags():
    posts = Post.query.all()
    return render_template('tags.html', posts=posts)


@posts.route("/post/<string:public_id>", methods=['POST', 'GET'])
@login_required
@check_confirmed
def post(public_id):
    page = request.args.get('page', 1, type=int)
    post = Post.query.filter_by(public_id=public_id)\
        .options(selectinload(Post.author), selectinload(Post.comment)).first()
    post.viewed = post.viewed + 1
    db.session.commit()
    posts = Post.query.order_by(Post.public_id.desc()).all()
    comments = Comment.query.filter_by(post_id=post.id, depth=0)\
        .order_by(Comment.pub_date.desc())\
        .paginate(page=page, per_page=20)
    rc = ReplyComment.query.order_by(ReplyComment.pub_date.desc()).all()
    form = CommentForm()
        
    if form.validate_on_submit():
        message = form.message.data
        depth = form.depth.data 
        
        comment = Comment(message=message, post_id=post.id, user_id=current_user.id, depth=depth)
        db.session.add(comment)
        post.comments = post.comments + 1
        db.session.commit()
        return redirect(url_for('posts.post', public_id=post.public_id))
    reply_form = ReplyForm()

    return render_template('post.html', post=post, rc=rc,
                           public_id=post.public_id, posts=posts,
                           comments=comments, form=form, reply_form=reply_form, title='Posts')


@posts.route("/post/<string:public_id>/comment/<int:comment_id>",
             methods=['GET', 'POST'])
@login_required
@check_confirmed
def reply_comment(public_id, comment_id):
    page = request.args.get('page', 1, type=int)
    post = Post.query.filter_by(public_id=public_id).first()
    parent_comment = Comment.query.filter_by(id=comment_id).first()
    rc = ReplyComment.query.filter_by(comment_id=parent_comment.id)\
        .order_by(ReplyComment.pub_date.desc()).paginate(page=page, per_page=20)
    reply_form = ReplyForm()
    
    if reply_form.validate_on_submit():
        reply_message = reply_form.content.data  # Use form data directly
        reply = ReplyComment(message=reply_message, comment=current_user,
                             post_id=post.id, comment_id=parent_comment.id)
        db.session.add(reply)
        parent_comment.replys = parent_comment.replys + 1
        db.session.commit()
        return redirect(url_for('posts.reply_comment',
                                public_id=post.public_id, comment_id=parent_comment.id))
    
    return render_template('reply.html', parent_comment=parent_comment,
                           post=post, reply_form=reply_form, rc=rc)


@posts.route("/post/<string:public_id>/update", methods=['GET', 'POST'])
@login_required
@check_confirmed
def update_post(public_id):
    post = Post.query.filter_by(public_id=public_id).first()
    comment = Comment.query.filter_by(post_id=post.id).all()
    rc = ReplyComment.query.filter_by(post_id=post.id).all()
    posk = Post.query \
        .order_by(Post.date_posted.desc()) \
        .paginate()
    pots = Post.query.filter_by(author=current_user) \
        .order_by(Post.date_posted.desc()) \
        .paginate()
    if post.author != current_user:
        abort(403)
    for i in rc:
        db.session.delete(i)
    for o in comment:
        db.session.delete(o)

    post.comments = post.comments - post.comments
    form = UpdatePostForm()
    if form.validate_on_submit():
        post.love = 0
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('posts.post', public_id=post.public_id))
    elif request.method == 'GET':

        form.content.data = post.content
    return render_template('create_post.html', title='Update Post',
                           form=form, legend='Update Post', posk=posk, pots=pots)


@posts.route("/post/<int:post_id>/delete", methods=['GET','POST'])
@login_required
@check_confirmed
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    comment = Comment.query.filter_by(post_id=post_id).all()
    rc = ReplyComment.query.filter_by(post_id=post.id).all()
    if post.author != current_user:
        abort(403)
    for i in rc:
        db.session.delete(i)
    for o in comment:
        db.session.delete(o)
    db.session.delete(post)
    delete_post_task.delay(public_id=post.public_id)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('main.home'))



@posts.route("/post/<string:public_id>/comment/<int:comment_id>/delete",
 methods=['POST'])
@login_required
@check_confirmed
def delete_comment(public_id, comment_id):
    post = Post.query.filter_by(public_id=public_id).first()
    comment = Comment.query.get_or_404(comment_id)
    cx = ReplyComment.query.filter_by(comment_id=comment_id).all()
    for i in cx:
        db.session.delete(i)
        db.session.commit()
    if comment.reply != current_user:
        abort(403)
    db.session.delete(comment)
    post.comments = post.comments - 1
    db.session.commit()
    return redirect(url_for('posts.post', public_id=post.public_id))



@posts.route("/following", methods=['GET', 'POST'])
@login_required
@check_confirmed
@cache.cached() 
def following():
    follow = Comment.query.filter_by(reply=current_user)\
    .order_by(Comment.pub_date.desc()).all()
    return render_template('following.html',follow=follow, title='My Activities')


@posts.route("/following/images", methods=['GET', 'POST'])
@login_required
@check_confirmed
@cache.cached() 
def image_following():
    posts = Media_Comments.query.filter_by(reple=current_user)\
    .order_by(Media_Comments.pub_date.desc()).all()

    return render_template('image_following.html',
     posts=posts, title='My Activities')


@posts.route("/following/videos", methods=['GET', 'POST'])
@login_required
@check_confirmed
@cache.cached() 

def video_following():
    posts = Media_Comment.query.filter_by(repli=current_user)\
    .order_by(Media_Comment.pub_date.desc()).all()

    return render_template('video_following.html', 
    posts=posts, title='My Activities')


@posts.route('/report/<int:post_id>')
def report(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('report.html', post_id=post.id)


@posts.route("/post/images/<string:plic_id>", methods=['POST', 'GET'])
@login_required
@check_confirmed
def img_post(plic_id):
    page = request.args.get('page', 1, type=int)
    images = Images.query.filter_by(plic_id=plic_id).first()
    form = CommentsForm()
    comments = Media_Comments.query.filter_by(images_id=images.id)\
    .order_by(Media_Comments.pub_date.desc()).paginate(
        page=page,
        per_page=20)
    if form.validate_on_submit():
        message = request.form.get('message')
        comment = Media_Comments(message=message, 
        images_id=images.id, reple=current_user)
        db.session.add(comment)
        images.comments = images.comments + 1
        db.session.commit()
        return redirect(request.url)
    return render_template('image_post.html', images=images,
     form=form, comments=comments)

@posts.route("/post/images/<string:plic_id>/comment/<int:media_comment_id>",
 methods=['GET','POST'])
@login_required
@check_confirmed
def reply_img(plic_id, media_comment_id):
    #data= request.form.get('text')
    page = request.args.get('page', 1, type=int)
    images = Images.query.filter_by(plic_id=plic_id).first()
    comment = Media_Comments.query.filter_by(id=media_comment_id).first()
    rc= MediaReplyComments.query.filter_by(media_comments_id=comment.id)\
    .order_by(MediaReplyComments.pub_date.desc()).paginate(page=page, per_page=20)
    form = ReplyForm()
    if form.validate_on_submit():
        rc = MediaReplyComments(message=form.message.data, 
        img_reply=current_user, media_comments_id=comment.id)
        db.session.add(rc)
        comment.replys=comment.replys + 1
        db.session.commit()
        return redirect(url_for('posts.reply_img', 
        plic_id=images.plic_id, media_comment_id=comment.id))
    return render_template('img_reply.html', 
    comment=comment, images=images, form=form, rc=rc)




@posts.route("/post/images/<int:images_id>/delete", methods=['GET', 'POST'])
@login_required
@check_confirmed
def delete_images(images_id):
    images = Images.query.get_or_404(images_id)
    comment = Media_Comments.query.filter_by(images_id=images.id).all()
    if images.imgs != current_user:
        abort(403)

    for o in comment:
        db.session.delete(o)
    db.session.delete(images)

    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('main.home'))


@posts.route("/post/images/<string:plic_id>/comment/<int:comment_id>/delete",
 methods=['POST', 'GET'])
@login_required
@check_confirmed
def delete_images_comment(plic_id, comment_id):
    images = Images.query.filter_by(plic_id=plic_id).first()
    comment = Media_Comments.query.get_or_404(comment_id)
    if comment.reple != current_user:
        abort(403)
    db.session.delete(comment)
    images.comments = images.comments - 1
    db.session.commit()
    return redirect(url_for('posts.img_post', plic_id=images.plic_id))


@posts.route("/post/videos/<string:publ_id>", methods=['POST', 'GET'])
@login_required
@check_confirmed
def vid_post(publ_id):
    page = request.args.get('page', 1, type=int)
    videos = Videos.query.filter_by(publ_id=publ_id).first()
    form = CommentsForm()
    comments = Media_Comment.query.filter_by(videos_id=videos.id)\
        .order_by(Media_Comment.pub_date.desc()).paginate(
        page=page,
        per_page=20)
    if form.validate_on_submit():
        message = request.form.get('message')
        comment = Media_Comment(message=message, videos_id=videos.id, repli=current_user)
        db.session.add(comment)
        videos.comments = videos.comments + 1
        db.session.commit()
        return redirect(request.url)
    return render_template('video_post.html', videos=videos, form=form, comments=comments)


@posts.route("/post/videos/<int:videos_id>/delete", methods=['GET', 'POST'])
@login_required
@check_confirmed
def delete_videos(videos_id):
    videos = Videos.query.get_or_404(videos_id)
    comment = Media_Comment.query.filter_by(videos_id=videos.id).all()
    if videos.vids != current_user:
        abort(403)

    for o in comment:
        db.session.delete(o)
    db.session.delete(videos)

    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('main.home'))


@posts.route("/post/videos/<string:publ_id>/comment/<int:comment_id>/delete",
 methods=['GET', 'POST'])
@login_required
@check_confirmed
def delete_videos_comment(publ_id, comment_id):
    videos = Videos.query.filter_by(publ_id=publ_id).first()
    comment = Media_Comment.query.get_or_404(comment_id)
    if comment.repli != current_user:
        abort(403)
    db.session.delete(comment)
    videos.comments = videos.comments - 1
    db.session.commit()
    return redirect(url_for('posts.vid_post', publ_id=videos.publ_id))

@posts.route("/post/video/<string:publ_id>/comment/<int:media_comment_id>",
 methods=['GET','POST'])
@login_required
@check_confirmed
def reply_video(publ_id, media_comment_id):
    #data= request.form.get('text')
    page = request.args.get('page', 1, type=int)
    videos = Videos.query.filter_by(publ_id=publ_id).first()
    comment = Media_Comment.query.filter_by(id=media_comment_id).first()
    rc= MediaReplyComment.query.filter_by(media_comment_id=comment.id)\
    .order_by(MediaReplyComment.pub_date.desc()).paginate(page=page, per_page=20)
    form = ReplyForm()
    if form.validate_on_submit():
        rc = MediaReplyComment(message=form.message.data,
         vid_reply=current_user, media_comment_id=comment.id)
        db.session.add(rc)
        comment.replys=comment.replys + 1
        db.session.commit()
        return redirect(url_for('posts.reply_video', 
        publ_id=videos.publ_id, media_comment_id=comment.id))
    return render_template('vid_reply.html', comment=comment,
     videos=videos, form=form, rc=rc)
