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
    # Subscribe to only the pattern. The pattern "chatroom:*" will
    # correctly catch both chatroom messages and the broadcast message.
    pubsub.psubscribe("chatroom:*")
    
    for message in pubsub.listen():
        if message['type'] == 'pmessage':
            # Note: The channel name is available in the message payload for pmessage type
            channel = message['channel']
            data = json.loads(message['data'])
            
            if channel == "chatroom:broadcast":
                # This is a broadcast message.
                data["room_id"] = "ADMIN"
                sio.emit("new_message", data)
            else:
                # This is a regular chatroom message.
                room_id = data['room_id']
                sio.emit("new_message", data, room=room_id)
        # We no longer need to check for message['type'] == 'message'
        # because we removed the direct subscription that would produce it.

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
