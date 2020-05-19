from flask import render_template, redirect, url_for, flash, request, abort, Blueprint, jsonify
from flaskblog import db
from flaskblog.posts.forms import PostForm, UpdatePostForm, CommentForm, ReplyForm
from flaskblog.models import Post, Comment, User
from flask_login import current_user, login_required
from flaskblog.posts.utils import save_img
import random
#from google.cloud import translate_v2 as translate

posts = Blueprint('posts', __name__)



@posts.route("/explore", methods=['GET', 'POST'])
@login_required
def explore():
    side = (Post.query.order_by(Post.comments.desc()).all()[0:100])
    x=random.shuffle(side)
    return render_template('explore.html', side=side)


@posts.route("/tags", methods=['GET','POST'])
def tags():


    return render_template('tags.html')





@posts.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        file = request.files['photo']
        pic_file = save_img(form.photo.data)
        post = Post( content=form.content.data, author=current_user, img_data=file.read(),
                    img_filename=pic_file)
        '''translate_client = translate.Client()

        text = form.content.data
        target = 'es'

        translation = translate_client.translate(
            text,
            target_language=target)

        print('Text:  ', text)

        print(u'Translation: {}'.format(translation['translatedText']))'''
        db.session.add(post)
        db.session.commit()

        return redirect(url_for('main.home'))
    return render_template('create_post.html', title='New Post',
                           form=form, legend='New Post')



@posts.route("/post/<int:post_id>", methods=['POST','GET'])
@login_required
def post(post_id):
    page = request.args.get('page', 1, type=int)
    post = Post.query.get_or_404(post_id)
    posts = Post.query.order_by(Post.id.desc()).all()
    comments= Comment.query.filter_by(post_id=post.id).order_by(Comment.pub_date.desc()).paginate(page=page, per_page=5)
    form= CommentForm()
    if request.method== 'POST' and form.validate_on_submit():
        message= request.form.get('message')
        comment= Comment(message=message, post_id=post.id, reply=current_user)

        db.session.add(comment)
        post.comments= post.comments+1
        db.session.commit()
        return redirect(request.url)
    return render_template('post.html', post=post, posts=posts, comments=comments, form=form)


@posts.route("/post/<int:post_id>/comment/<int:comment_id>", methods=['POST'])
def reply_comment(post_id, comment_id):
    form2 = ReplyForm()
    post = Post.query.get_or_404(post_id)
    comment=Comment.query.get_or_404(comment_id)
    commenta = Comment.query.filter_by(post_id=post.id, reply_message=Comment.reply_message).order_by(
        Comment.pub_date.desc()).all()
    if request.method == 'POST' and form2.validate_on_submit():
        reply_messag = request.form.get('replys')
        comment2 = Comment(reply_message=reply_messag, post_id=post.id, comment_id=comment.id, reply=current_user)
        db.session.add(comment2)
        db.session.commit()

    return redirect(url_for(request.url, post_id=post.id, commenta=commenta, form2=form2))







"""

    '''translate_client = translate.Client()

    text = Post.query.filter_by(id=post.content)
    target = 'fr'

    translation = translate_client.translate(
        text,
        target_language=target)

    print('Text:  ', text)

    print(u'Translation: {}'.format(translation['translatedText']))'''
@posts.route("/post/create-entry", methods=['GET', 'POST'])
@login_required
def create_entry():
    req = request.get_json()

    print(req)

    res = make_response(jsonify(req), 200)

    return res
"""


@posts.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    comment = Comment.query.filter_by(post_id=post_id).all()
    if post.author != current_user:
        abort(403)
    for o in comment:
        db.session.delete(o)
    post.comments = post.comments - post.comments
    form = UpdatePostForm()
    if form.validate_on_submit():

        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('posts.post', post_id=post.id))
    elif request.method == 'GET':

        form.content.data = post.content
    return render_template('create_post.html', title='Update Post',
                           form=form, legend='Update Post')


@posts.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    comment = Comment.query.filter_by(post_id=post_id).all()
    if post.author != current_user:
        abort(403)

    for o in comment:
        db.session.delete(o)
    db.session.delete(post)

    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('main.home'))

@posts.route("/post/<int:post_id>/comment/<int:comment_id>/delete", methods=['POST'])
@login_required
def delete_comment(post_id, comment_id):
    post = Post.query.get_or_404(post_id)
    comment=Comment.query.get_or_404(comment_id)
    if comment.reply != current_user:
        abort(403)
    db.session.delete(comment)
    post.comments = post.comments - 1
    db.session.commit()
    return redirect(url_for('posts.post', post_id=post.id))

@posts.route("/following", methods=['GET','POST'])
def following():
    posts = Comment.query.filter_by(reply=current_user).order_by(Comment.pub_date.desc()).all()


    return render_template('following.html', posts=posts)
