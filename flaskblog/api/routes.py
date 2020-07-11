# app.py
from operator import itemgetter
import requests
from flask import request, jsonify, Blueprint
from flaskblog.database import db_session
from flaskblog.model import User, Channel, Message
from flask_jwt_extended import jwt_required, create_access_token
from textblob import TextBlob

import pusher

from flaskblog.models import Admin, AdminSchema, UserSchema

pusher = pusher.Pusher(
    app_id="1026652",
    key="e64950608e34eabafaf1",
    secret="9652c7e4f3fe200b5fb2",
    cluster="mt1",
    ssl=True)

api = Blueprint('api', __name__)


@api.route('/api')
def index():
    return jsonify("Ping Pong!")


@api.route('/api/login', methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    user = User.query.filter_by(username=username).first()

    if not user:
        return jsonify({
            "status": "failed",
            "message": "Failed getting user"
        }), 401

    # Generate a token
    access_token = create_access_token(identity=username)

    return jsonify({
        "status": "success",
        "message": "login successful",
        "data": {
            "id": user.id,
            "token": access_token,
            "username": user.username
        }
    }), 200


@api.route('/api/request_chat', methods=["POST"])
def request_chat():
    request_data = request.get_json()
    from_user = request_data.get('from_user', '')
    to_user = request_data.get('to_user', '')
    to_user_channel = "private-notification_user_%s" % (to_user)
    from_user_channel = "private-notification_user_%s" % (from_user)

    # check if there is a channel that already exists between this two user
    channel = Channel.query.filter(Channel.from_user.in_([from_user, to_user])) \
        .filter(Channel.to_user.in_([from_user, to_user])) \
        .first()
    if not channel:
        # Generate a channel...
        chat_channel = "private-chat_%s_%s" % (from_user, to_user)

        new_channel = Channel()
        new_channel.from_user = from_user
        new_channel.to_user = to_user
        new_channel.name = chat_channel
        db_session.add(new_channel)
        db_session.commit()
    else:
        # Use the channel name stored on the database
        chat_channel = channel.name

    data = {
        "from_user": from_user,
        "to_user": to_user,
        "from_user_notification_channel": from_user_channel,
        "to_user_notification_channel": to_user_channel,
        "channel_name": chat_channel,
    }

    # Trigger an event to the other user
    pusher.trigger(to_user_channel, 'new_chat', data)

    return jsonify(data)


@api.route("/api/pusher/auth", methods=["POST"])
@jwt_required
def pusher_authentication():
    channel_name = request.form.get('channel_name')
    socket_id = request.form.get('socket_id')

    auth = pusher.authenticate(
        channel=channel_name,
        socket_id=socket_id
    )

    return jsonify(auth)


@api.route("/api/send_message", methods=["POST"])
@jwt_required
def send_message():
    request_data = request.get_json()
    from_user = request_data.get('from_user', '')
    to_user = request_data.get('to_user', '')
    message = request_data.get('message', '')
    channel = request_data.get('channel')

    new_message = Message(message=message, channel_id=channel)

    new_message.from_user = from_user
    new_message.to_user = to_user
    db_session.add(new_message)
    db_session.commit()

    message = {
        "from_user": from_user,
        "to_user": to_user,
        "message": message,
        "channel": channel,
        "sentiment": getSentiment(message)
    }

    # Trigger an event to the other user
    pusher.trigger(channel, 'new_message', message)

    return jsonify(message)


@api.route('/api/users')
def users():
    users = User.query.all()

    return jsonify(
        [{"id": user.id, "userName": user.username} for user in users]
    ), 200

@api.route('/api/get_message/<channel_id>')
@jwt_required
def user_messages(channel_id):
    messages = Message.query.filter(Message.channel_id == channel_id).all()

    return jsonify([
        {
            "id": message.id,
            "message": message.message,
            "to_user": message.to_user,
            "channel_id": message.channel_id,
            "from_user": message.from_user,
            "sentiment": getSentiment(message.message)
        }
        for message in messages
    ])


def getSentiment(message):
    text = TextBlob(message)
    return {'polarity': text.polarity}


@api.route('/api/problems')
def problems():
    probs = Admin.query.all()
    admins_schema = AdminSchema(many=True)
    res = admins_schema.dump(probs)
    result = list(map(itemgetter('adm', 'report_a_problem'), res))
    return jsonify({'problems': result})


@api.route('/api/search', methods=['GET', 'POST'])
def search():
    # db.session.query(User).filter(User.username.data == 1).all()
    results = User.query.all()
    user_schema = UserSchema(many=True)
    res = user_schema.dump(results)
    result = list(map(itemgetter('email', 'username'), res))
    if 'Stephen Ford' in result:
        print('found the name Stephen Ford')
    else:
        print('No Match')
    '''ip_request = requests.get('https://get.geojs.io/v1/ip.json')
    my_ip = ip_request.json()['ip']
    print(my_ip)

    geo_request_url = 'https://get.geojs.io/v1/ip/geo/' + my_ip + '.json'
    geo_request = requests.get(geo_request_url)
    geo_datas = geo_request.json()
    geo_data = geo_datas['country']'''
    return jsonify({'user': result} )


''', geo_data'''


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

@api.route('/api/list', methods=['GET'])
def api_list():
    return jsonify(Languages)
