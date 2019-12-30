
from flask import render_template ,request,  Blueprint

from flaskblog.models import Post
from google.cloud import translate_v2 as translate



main= Blueprint('main', __name__)


@main.route('/')
@main.route('/home')

def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=8)


    '''translate_client = translate.Client()

    text = Post.query.get(Post.content)
    target = 'fr'

    translation = translate_client.translate(
        text,
        target_language=target)

    print('Text:  ', text)

    print(u'Translation: {}'.format(translation['translatedText']))
'''

    return render_template('home.html', posts= posts)



