
from flask import render_template, request, Blueprint, json, url_for, redirect
from flask_login import login_required

from flaskblog.main.form import Searchform
from flaskblog.models import Post, User
#from google.cloud import translate_v2 as translate
from flask import Flask, render_template, request, jsonify
'''from pusher import Pusher, pusher
import uuid
'''



main= Blueprint('main', __name__)


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


@main.route('/home')
@login_required

def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=8)
    side= (Post.query.order_by(Post.comments.desc()).all()[0:10])
    form= Searchform()




    '''def convert_to_dict(obj):
        """
        A function takes in a custom object and returns a dictionary representation of the object.
        This dict representation includes meta data such as the object's module and class names.
        """

        #  Populate the dictionary with object meta data
        obj_dict = {
            "__class__": obj.__class__.__name__,
            "__module__": obj.__module__
        }

        #  Populate the dictionary with object properties
        obj_dict.update(obj.__dict__)

        return obj_dict


    translate_client = translate.Client()

    text = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=8)

    target = 'fr'

    translation = translate_client.translate(
        text,
        target_language=target)

    data = json.dumps(text, default=convert_to_dict)

    print(data)

    #print(u'Translation: {}'.format(translation['translatedText']))
    
'''



    return render_template('home.html', posts=posts, side=side, form=form)

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

@main.route('/search')

def search():
    return render_template('search.html')