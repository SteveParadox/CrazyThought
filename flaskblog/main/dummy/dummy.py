from flaskblog import db, app
from flask import *
from flaskblog.models import *
import random
import shortuuid
import string
from flaskblog.tasks import data_task

dummy = Blueprint('dummy', __name__)

sample_content = [
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
    "Sed ut perspiciatis unde omnis iste natus error sit voluptatem.",
    "Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit.",
    "Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet.",
    "Consectetur, adipisci velit, sed quia non numquam eius modi tempora incidunt.",
]

@dummy.route('/dummy')
def dumm():
    for _ in range(100):
        random.shuffle(sample_content)
        post = Post(
            public_id=str(shortuuid.uuid()),
            content=sample_content[0],
            comments=random.randint(0, 1000000),
            love=random.randint(0, 100000000),
            user_id=random.randint(1, 90), 
            viewed=random.randint(0, 1000),
            extra="",
        )

        db.session.add(post)
    db.session.commit()
    data_task.delay()
    return redirect(url_for('main.home'))

def generate_random_string(length):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

@dummy.route('/user/dummy')
def user_dummy():
    for _ in range(100):
        username = generate_random_string(8)
        email = generate_random_string(10) + '@example.com'
        password = generate_random_string(12)

        user = User(
            username=username,
            email=email,
            password=password,
        )

        db.session.add(user)

    # Commit the changes to the database
    db.session.commit()
    return redirect(url_for('main.home'))

@dummy.route('/pass')
def notting():
    return "Hello"

@dummy.route('/create_tables')
def create_tables():
    with app.app_context():
        db.create_all()
    return 'Database tables created successfully'