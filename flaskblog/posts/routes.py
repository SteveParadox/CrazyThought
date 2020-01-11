from flask import render_template, redirect, url_for, flash, request, abort, Blueprint
from flaskblog import db
from flaskblog.posts.forms import PostForm
from flaskblog.models import Post, Comment
from flask_login import current_user, login_required
from flaskblog.posts.utils import save_img
#from google.cloud import translate_v2 as translate

posts = Blueprint('posts', __name__)



@posts.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        file = request.files['photo']
        pic_file = save_img(form.photo.data)
        post = Post(title=form.title.data, content=form.content.data, author=current_user, img_data=file.read(),
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
        flash('Your post has been created!', 'success')
        return redirect(url_for('main.home'))
    return render_template('create_post.html', title='New Post',
                           form=form, legend='New Post')


@posts.route("/post/<int:post_id>", methods=['POST', 'GET'])
@login_required
def post(post_id):
    page = request.args.get('page', 1, type=int)
    post = Post.query.get_or_404(post_id)
    posts = Post.query.order_by(Post.id.desc()).all()
    comments = Comment.query.filter_by(post_id=post.id).order_by(Comment.pub_date.desc()).paginate(page=page,
                                                                                                   per_page=5)
    side = (Post.query.order_by(Post.comments.desc()).all())
    dox = len(side)

    '''translate_client = translate.Client()

    text = Post.query.filter_by(id=post.content)
    target = 'fr'

    translation = translate_client.translate(
        text,
        target_language=target)

    print('Text:  ', text)

    print(u'Translation: {}'.format(translation['translatedText']))'''

    if request.method == 'POST':
        message = request.form.get('message')
        comment = Comment(message=message, post_id=post.id, reply=current_user)

        db.session.add(comment)
        post.comments = post.comments + 1
        flash('your comment has been submitted', 'success')
        db.session.commit()
        return redirect(request.url)
    return render_template('post.html', title=post.title, post=post, posts=posts, comments=comments, side=side)


"""

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
    form = PostForm()
    if form.validate_on_submit():
        pic_file = save_img(form.photo.data)
        post.title = form.title.data
        post.content = form.content.data
        post.img_filename = pic_file
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('posts.post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
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
