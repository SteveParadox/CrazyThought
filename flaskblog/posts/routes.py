from flask import render_template, redirect, url_for, flash, request, abort, Blueprint
from flaskblog import db
from flaskblog.posts.forms import PostForm
from flaskblog.models import Post, Comment
from flask_login import current_user, login_required
from flaskblog.posts.utils import save_img



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
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('main.home'))
    return render_template('create_post.html', title='New Post',
                           form=form, legend='New Post')






@posts.route("/post/<int:post_id>", methods=['POST','GET'])
@login_required
def post(post_id):
    post = Post.query.get_or_404(post_id)
    posts = Post.query.order_by(Post.id.desc()).all()
    comments= Comment.query.filter_by(post_id=post.id).all()
    com= Comment.query.order_by(Comment.pub_date.desc()).all()

    if request.method== 'POST':
        message= request.form.get('message')
        comment= Comment(message=message, post_id=post.id, name=current_user.username)

        db.session.add(comment)
        post.comments= post.comments+1
        flash('your comment has been submitted', 'success')
        db.session.commit()
        return redirect(request.url)
    return render_template('post.html', title=post.title, post=post, posts=posts, comments=comments, com=com)



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
    if post.author != current_user:
        abort(403)
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
    comment = Comment.query.get_or_404(id)
    if post.author != current_user:
        abort(403)
    comment= Comment(comment_post_id=comment.post_id, comment_id=comment.id)
    db.session.delete(post)
    db.session.delete(comment)

    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('main.home'))





@posts.route("/post/fashion", methods=['GET', 'POST'])
@login_required
def fashion():
    posts = Post.query.all()
    return render_template('fashion.html', posts=posts)


@posts.route("/post/fineart", methods=['GET', 'POST'])
@login_required
def fineart():
    return render_template('fineart.html')


@posts.route("/post/landscape", methods=['GET', 'POST'])
@login_required
def landscape():
    return render_template('landscape.html')


@posts.route("/post/macro", methods=['GET', 'POST'])
@login_required
def macro():
    return render_template('macro.html')


@posts.route("/post/photoshop", methods=['GET', 'POST'])
@login_required
def photoshop():
    return render_template('photoshop.html')


@posts.route("/post/photojournalism", methods=['GET', 'POST'])
@login_required
def photojournalism():
    return render_template('photojournalism.html')


@posts.route("/post/portraiture", methods=['GET', 'POST'])
@login_required
def portraiture():
    return render_template('portraiture.html')


@posts.route("/post/wedding", methods=['GET', 'POST'])
@login_required
def wedding():
    return render_template('wedding.html')


@posts.route("/post/wildlife", methods=['GET', 'POST'])
@login_required
def wildlife():
    return render_template('wildlife.html')
