from flask import Flask, render_template
from flask_socketio import SocketIO, emit, join_room, leave_room

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

rooms_users = {}  # Dictionary to keep track of users in rooms

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']

    if room not in rooms_users:
        rooms_users[room] = []
    rooms_users[room].append(username)
    
    join_room(room)
    emit('message', {'msg': f'{username} has joined the room.'}, room=room)
    emit('update_users', {'users': rooms_users[room]}, room=room)

@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']

    if room in rooms_users and username in rooms_users[room]:
        rooms_users[room].remove(username)
        if not rooms_users[room]:
            del rooms_users[room]

    leave_room(room)
    emit('message', {'msg': f'{username} has left the room.'}, room=room)
    emit('update_users', {'users': rooms_users.get(room, [])}, room=room)

@socketio.on('code_update')
def handle_code_update(data):
    room = data['room']
    code = data['code']
    emit('code_update', {'code': code}, room=room)

@socketio.on('typing')
def handle_typing(data):
    room = data['room']
    username = data['username']
    emit('typing', {'username': username}, room=room)

if __name__ == '__main__':
    socketio.run(app, debug=True)
