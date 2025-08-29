import eventlet
eventlet.monkey_patch()

import socketio
import redis
import json
import threading

sio = socketio.Server(cors_allowed_origins='*')
app = socketio.WSGIApp(sio)

r = redis.Redis(host='redis', port=6379, decode_responses=True)

def redis_listener():
    pubsub = r.pubsub()
    pubsub.psubscribe("chatroom:*")
    for message in pubsub.listen():
        if message['type'] == 'pmessage':
            data = json.loads(message['data'])
            room_id = data['room_id']
            sio.emit("new_message", data, room=room_id)

@sio.event
def connect(sid, environ):
    print("Client connected:", sid)

@sio.event
def join(sid, data):
    room_id = data.get("room_id")
    sio.enter_room(sid, room_id)
    print(f"Client {sid} joined room {room_id}")

@sio.event
def disconnect(sid):
    print("Client disconnected:", sid)

# Start Redis listener in background
threading.Thread(target=redis_listener, daemon=True).start()

# Start the server
if __name__ == "__main__":
    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 5000)), app)

