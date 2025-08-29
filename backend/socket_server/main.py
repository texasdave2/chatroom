import socketio
import redis
import json
import threading

# Create a Socket.IO server instance
sio = socketio.Server(cors_allowed_origins='*')
app = socketio.WSGIApp(sio)

# Connect to Redis
r = redis.Redis(host='redis', port=6379, decode_responses=True)

# Redis listener thread
def redis_listener():
    pubsub = r.pubsub()
    pubsub.psubscribe("chatroom:*")
    for message in pubsub.listen():
        if message['type'] == 'pmessage':
            data = json.loads(message['data'])
            room_id = data['room_id']
            sio.emit("new_message", data, room=room_id)

# Socket.IO event handlers
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

# Start Redis listener in a background thread
threading.Thread(target=redis_listener, daemon=True).start()

