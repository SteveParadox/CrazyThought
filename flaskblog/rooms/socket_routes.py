from datetime import datetime
import shortuuid
from flask import Blueprint, redirect, render_template, url_for, jsonify
from flask_login import login_required, current_user
from flask_socketio import join_room, leave_room, close_room, emit
from flaskblog import io, db, cache
from flaskblog.models import Room, Messages, MessagesSchema
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

sock = Blueprint('sock', __name__)

class NicknameForm(FlaskForm):
    nickname = StringField('Nickname', validators=[DataRequired()])
    submit = SubmitField('Create')

@sock.route('/chat', methods=['GET', 'POST'])
def chat():
    rooms = Room.query.order_by(Room.created.desc()).all()
    form = NicknameForm()
    if form.validate_on_submit():
        created_room = str(shortuuid.uuid())
        host = current_user.username
        new_room = Room(nickname=form.nickname.data, unique_id=created_room, host=host, admin=True)
        db.session.add(new_room)
        db.session.commit()
        return redirect(url_for('sock.room', room_id=created_room))
    return render_template('chat.html', rooms=rooms, form=form)

@sock.route('/msx')
def _():
    messages = Messages.query.all()
    messages_schema = MessagesSchema(many=True)
    res = messages_schema.dump(messages)
    return jsonify(res)

@sock.route('/rooms')
@cache.cached()
def my_rooms():
    my_room = Room.query.filter_by().all()

    return render_template('rooms.html', my_room=my_room)


@sock.route('/group/<string:room_id>')
def room(room_id):
    active_room = Room.query.filter_by(unique_id=room_id).first()
    message_history = db.session.query(Messages.username, Messages.message, Messages.date) \
        .join(Room, Room.id == Messages.room_id) \
        .filter(Room.unique_id == room_id).all()
    return render_template('room.html', room_id=room_id, message_history=message_history, active_room=active_room)

@io.on("connect")
def on_connect():
    print("Socket connected!")
    emit('resp', {'message': 'connected'})


@io.on('online')
def online(data):
    username = data.get('username')
    if username:
        emit('status_change', {'username': username, 'status': 'online'}, broadcast=True)

@io.on("join_user")
def on_new_user(data):
    room_id = data['room_id']
    active_room = Room.query.filter_by(unique_id=room_id).first()
    join_room(active_room.unique_id)
    emit("New_user_joined", {"message": f"{data['name']} has joined the room"}, room=active_room.unique_id, broadcast=True)

@io.on('joined')
def joined_room(data):
    room_id = data['room_id']
    active_room = Room.query.filter_by(unique_id=room_id).first()
    emit('joined_room', {'username': data['name'], 'room': active_room.unique_id, 'status': 'joined'},
         room=active_room.unique_id, broadcast=True)

@io.on("group_message")
def on_new_message(message):
    room_id = message['room_id']
    active_room = Room.query.filter_by(unique_id=room_id).first()
    if active_room:
        new_message = Messages(room_id=active_room.id, username=message["name"], date=datetime.now(), message=message['message'])
        db.session.add(new_message)
        db.session.commit()
        emit('New', {
            "sender": message['name'],
            "time": datetime.now().strftime("%a %b %d %H:%M:%S "),
            "data": message['message'],
        }, room=active_room.unique_id, broadcast=True)
    else:
        emit('New_group_Message', {'message': 'Room not found'})

from flask import request

@io.on("get_message_history")
def get_message_history(data):
    room_id = data.get('room_id')
    active_room = Room.query.filter_by(unique_id=room_id).first()
    date_format = '%Y-%m-%d %H:%M:%S.%f'
    if active_room:
        message_history = db.session.query(Messages.username, Messages.message, Messages.date) \
            .join(Room, Room.id == Messages.room_id) \
            .filter(Room.unique_id == room_id).all()

        # Convert the Row objects to a list of dictionaries
        message_history_json = [
            {'username': message[0], 'message': message[1], 'date': message[2][:-7]}
            for message in message_history
        ]
        print(message_history_json)
        io.emit("message_history", message_history_json, room=request.sid)
    else:
        io.emit("message_history", [], room=request.sid)  # Empty history if room not found

@io.on("leave_room")
def on_leave_room(data):
    room_id = data['room_id']
    name = data['name']
    active_room = Room.query.filter_by(unique_id=room_id).first()
    leave_room(active_room.unique_id)
    if name == active_room.host:
        close_room(active_room.unique_id)
        db.session.delete(active_room)
        db.session.commit()
        return redirect(url_for("api.home"))
    emit("Left_user", {"message": f"{name} has left the room"}, room=active_room.unique_id, broadcast=True)

@io.on('disconnect')
def disconnect():
    emit("disconnected", {"message": 'Disconnected'})
