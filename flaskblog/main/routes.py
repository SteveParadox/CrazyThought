import time
from operator import itemgetter

import requests
from flask import Blueprint, jsonify, url_for, redirect
# from google.cloud import translate_v2 as translate
from flask import render_template, request
from flask_login import login_required, current_user

from flaskblog import db
from flaskblog.main.form import Searchform, SharePostForm
from flaskblog.models import Post, User, UserSchema, Business
from flaskblog.posts.forms import PostForm
from flaskblog.users.decorator import check_confirmed

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
    das= post.content


    if form.is_submitted():
        poss = Post(content=form.content.data, author=current_user)
        db.session.add(poss)
        db.session.commit()

        return redirect(url_for('main.home', post_id=post.id))
    return render_template('share.html', title='Share Post', form=form,
                           legend='Share Post', post_id=post.id, post=post, das=das)


@main.route('/home', methods=['GET', 'POST'])
@login_required
@check_confirmed
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=50)

    # ejd= share_post(23)

    pots = Post.query.filter_by(author=current_user) \
        .order_by(Post.date_posted.desc()) \
        .paginate()
   
    post = Post.query.order_by(Post.content.desc()).all()
    gry = (Post.query.order_by(Post.content).all())
    form = PostForm()

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

        return redirect(url_for('main.home'))

    return render_template('home.html', posts=posts, pots=pots,  reload=time.time(), form=form, post=post)


@main.route('/about', methods=['GET', 'POST'])
def about():
    return render_template('about.html')


'''
@main.route('/feed')
def feed():
    return render_template('feed.html')
    
'''


@main.route('/tos')
def tos():
    return render_template('tos.html')


@main.route('/cookies')
def cookies():
    return render_template('cookies.html')


@main.route('/search', methods=['GET', 'POST'])
def search():
    searchbox = request.form.get("livebox")
    # db.session.query(User).filter(User.username.data == 1).all()
    results = User.query.all()
    user_schema = UserSchema(many=True)
    res = user_schema.dump(results)
    result = list(map(itemgetter('email', 'username'), res))
    if 'Stephen Ford' in result:
        print('found the name Stephen Ford')
    else:
        print('No Match')
    ip_request = requests.get('https://get.geojs.io/v1/ip.json')
    my_ip = ip_request.json()['ip']
    print(my_ip)

    geo_request_url = 'https://get.geojs.io/v1/ip/geo/' + my_ip + '.json'
    geo_request = requests.get(geo_request_url)
    geo_datas = geo_request.json()
    geo_data = geo_datas['country']
    return jsonify({'user': result}, geo_data)


'''   x = result["username"]
    x = thisdict.get("model")'''


@main.route('/searchfile', methods=['GET', 'POST'])
@check_confirmed
def searchfile():
    form = Searchform()
    results = User.query.all()
    user_schema = UserSchema(many=True)
    res = user_schema.dump(results)
    result = list(map(itemgetter('username'), res))
    paxx = form.livebox.data
    pots = Post.query.filter_by(author=current_user) \
        .order_by(Post.date_posted.desc()) \
        .paginate()


    if paxx in result:
        return render_template('search.html', form=form, paxx=paxx,pots=pots, result=result, author=paxx)
    else:
        return render_template('search.html', form=form, pots=pots)


'''


@main.route('/search_results/<query>')
@login_required
def search_results(query):
    results = User.query.whoosh_search(query).all()
    return render_template('search_results.html', query=query, results=results)

'''


@main.route('/max')
def index():
    return jsonify("Pong!")


Languages = [
    {
        'python': '1st rated',
        'javascript': 'i hate but 2nd rated',
        'c++': 'my ex crush but 3rd rated',
        'java': 'just there as my 4th rated',

    },
    {
        'vue.js': '1st rated',
        'jquery': 'i hate but 2nd rated',
        'react.js': 'my ex crush but 3rd rated',
        'vanilla.js': 'just there as my 4th rated',

    }
]


@main.route('/total')
def total():
    return render_template('total.html')


@main.route('/home/list', methods=['GET'])
def api_list():
    return jsonify(Languages)
