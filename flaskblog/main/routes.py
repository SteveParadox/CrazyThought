import time
import random

from flask import Blueprint, jsonify, url_for, redirect, json, flash
from flask_login import login_required, current_user


from flaskblog import db, abort
from flaskblog.main.form import Searchform, SharePostForm, GetPostForm
from flaskblog.models import Post, User, Comment
# from google.cloud import translate_v2 as translate
from flask import render_template, request

from flaskblog.posts.forms import PostForm

'''from pusher import Pusher, pusher.
import uuid
'''

main = Blueprint('main', __name__)

'''
pusher_client = pusher.Pusher(
  app_id='926605',
  key='1a1e24764be2a75fa3eb',
  secret='eb8037169d3d98297964',
  cluster='eu',
  ssl=True
)
'''


@main.route('/')
def loader():
    return render_template('loader.html')

''' form2 = GetPostForm()
form2.content.data = post.content'''
@main.route("/post/share/<int:post_id>", methods=['GET', 'POST'])
@login_required
def share_post(post_id):
    post = Post.query.get_or_404(post_id)
    form = SharePostForm()



    if form.is_submitted():
        poss = Post(content=form.content.data, author=current_user)


        db.session.add(poss)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('main.home', post_id=post.id))
    return render_template('share.html', title='Share Post', form=form,
                           legend='Share Post', post_id=post.id, post=post)





@main.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=30)

   #ejd= share_post(23)


    side = (Post.query.order_by(Post.comments.desc()).all()[0:10])
    gra = Comment.query.order_by(Comment.pub_date.desc()).all()
    gry = (Post.query.order_by(Post.content).all())
    form = PostForm()
    gray = random.choice(gry)

    if form.validate_on_submit():
        post = Post(content=form.content.data, author=current_user)
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

    return render_template('home.html', posts=posts, side=side, reload=time.time(), gray=gray, form=form)


@main.route('/search', methods=['GET', 'POST'])
def search():
    form = Searchform()


    return render_template('search.html', form=form)


'''
@main.route('/feed')
def feed():
    return render_template('feed.html')
    
'''

'''
@main.route('/search', methods=['GET', 'POST'])
def search():
    form = Searchform()
    if request.method == 'POST' and form.validate_on_submit(): 
        return redirect(url_for('search_results', query=form.search.data))
    return render_template('home.html', form=form)


@main.route('/search_results/<query>')
@login_required
def search_results(query):
    results = User.query.whoosh_search(query).all()
    return render_template('search_results.html', query=query, results=results)

'''
