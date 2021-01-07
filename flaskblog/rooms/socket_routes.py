import datetime
import shortuuid

from flask import Blueprint, redirect, render_template, url_for, jsonify
from flask_cors import cross_origin
from flask_login import login_required, current_user
from flask_socketio import join_room, leave_room, close_room
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

from flaskblog import io, db
from flaskblog.models import Room, Messages, MessagesSchema

sock = Blueprint('sock', __name__)


class NicknameForm(FlaskForm):
    nickname = StringField(DataRequired())
    submit = SubmitField('Create')


@sock.route('/chat', methods=['GET', 'POST'])
def chat():
    room = Room.query.order_by(Room.created.desc()).all()
    form = NicknameForm()
    if form.validate_on_submit():
        created_room = str(shortuuid.uuid())
        host = current_user.username
        roomx = Room()
        roomx.nickname = form.nickname.data
        roomx.unique_id = created_room
        roomx.host = host
        roomx.admin = True
        db.session.add(roomx)
        db.session.commit()
        return redirect(url_for('sock.room', room_id=created_room))
    return render_template('chat.html', room=room, form=form)


@sock.route('/msx')
def _():
    mesg = Messages.query.all()
    messages_schema = MessagesSchema(many=True)
    res = messages_schema.dump(mesg)
    return jsonify(res)


@sock.route('/group/<string:room_id>')
def room(room_id):
    active_ = Room.query.filter_by(unique_id=room_id).first()
    message_history = Messages.query.filter_by(msgs=active_).all()
    return render_template('rooms.html', room_id=room_id, message_history=message_history, active_=active_)


@io.on("connect")
def on_connect():
    print('goal')
    io.emit('resp', {'message': 'connected'})


@io.on('online')
def online(data):
    print(current_user.username)
    io.emit('status_change', {'username': current_user.username, 'status': 'online'}, broadcast=True)


# joining room
@io.on("join_user")
def on_new_user(data):
    room = data['room_id']
    print(room)
    active_ = Room.query.filter_by(unique_id=room).first()

    '''for i in message_history:
        io.emit('history',
                {
                    'username': i.username,
                    'message': i.message,
                    'time': i.date
                }
                , room=active_.unique_id)'''
    join_room(active_.unique_id)


@io.on('joined')
def joined_room(data):
    room = data['room_id']
    active = Room.query.filter_by(unique_id=room).first()

    io.emit('joined_room', {'username': data['name'], 'room': active.unique_id, 'status': 'joined'},
            room=active.unique_id, broadcast=True)


# send message to joined room
@io.on("group_message")
def on_new_message(message):
    room = message['room_id']
    print(str(message))
    active = Room.query.filter_by(unique_id=room).first()
    mssg = Messages(msgs=active)
    mssg.username = message["name"]
    mssg.date = datetime.datetime.now().strftime("%a %b %d %H:%M:%S ")
    mssg.message = message['message']
    db.session.add(mssg)
    db.session.commit()

    if active:
        io.emit('New_group_Message', {'message': f'New message from {message["name"]}'}, room=active.unique_id,
                broadcast=True)
        io.emit("New", {
            "sender": message['name'],
            "time": datetime.datetime.now().strftime("%a %b %d %H:%M:%S "),
            "data": message['message'],
        }, room=active.unique_id, broadcast=True)
    else:
        io.emit('New_group_Message', {'message': f'Room not found'})


# leave room
@io.on("leave_room")
def on_leave_room(data):
    room = data['room_id']
    name = data['name']
    active = Room.query.filter_by(unique_id=room).first()
    leave_room(active.unique_id)
    if name == active.host:
        close_room(active.unique_id)
        db.session.delete(active.unique_id)
        return redirect(url_for("api.home"))
    io.emit("Left_user", {"message": f"{name} has left the room"}, room=active.unique_id, broadcast=True)


@io.on('disconnect')
def disconnect():
    io.emit("disconnected",
            {"message": 'Disconnected'})
