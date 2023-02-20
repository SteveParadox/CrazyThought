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
    message_history = db.session.query(Messages.username, Messages.message, Messages.date)\
                    .join(Room, Room.id == Messages.room_id)\
                    .filter(Room.unique_id == room_id).all()
    return render_template('rooms.html', room_id=room_id, message_history=message_history, active_=active_)


@io.on("connect")
def on_connect():
    print('goal')
    io.emit('resp', {'message': 'connected'})


@io.on('online')
def online(data):
    username = data.get('username')
    if username:
        io.emit('status_change', {'username': username, 'status': 'online'}, broadcast=True)



# joining room
@io.on("join_user")
def on_new_user(data):
    room = data['room_id']
    print(room)
    active_room = Room.query.filter_by(unique_id=room).first()

    join_room(active_room.unique_id)
    io.emit("New_user_joined", {"message": f"{data['name']} has joined the room"}, room=active_room.unique_id, broadcast=True)



@io.on('joined')
def joined_room(data):
    room = data['room_id']
    active = Room.query.filter_by(unique_id=room).first()

    io.emit('joined_room', {'username': data['name'], 'room': active.unique_id, 'status': 'joined'},
            room=active.unique_id, broadcast=True)




# send message to joined room
@io.on("group_message")
def on_new_message(message):
    room_id = message['room_id']
    print(str(message))
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
        emit('New_group_Message', {'message': f'Room not found'})




# leave room
@io.on("leave_room")
def on_leave_room(data):
    room = data['room_id']
    name = data['name']
    active = Room.query.filter_by(unique_id=room).first()
    leave_room(active.unique_id)
    if name == active.host:
        close_room(active.unique_id)
        db.session.delete(active)
        db.session.commit()
        return redirect(url_for("api.home"))
    io.emit("Left_user", {"message": f"{name} has left the room"}, room=active.unique_id, broadcast=True)


@io.on('disconnect')
def disconnect():
    io.emit("disconnected",
            {"message": 'Disconnected'})
