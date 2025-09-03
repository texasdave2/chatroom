import eventlet
eventlet.monkey_patch()

import socketio
import redis
import json
import threading
import os
import google.generativeai as genai

# Configure the LLM
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

sio = socketio.Server(cors_allowed_origins='*')
app = socketio.WSGIApp(sio)

r = redis.Redis(host='redis', port=6379, decode_responses=True)

# LLM analysis functions, now in the background worker
def get_mood_from_llm(text: str) -> str:
    """Sends text to an LLM for mood analysis."""
    prompt = f"Analyze the following chat message and classify its mood as either 'happy', 'sad', or 'neutral'. Respond with only the label. Message: '{text}'"
    try:
        response = model.generate_content(prompt, generation_config={"temperature": 0.0})
        return response.text.strip().lower()
    except Exception as e:
        print(f"LLM analysis failed: {e}")
        return "neutral"

def get_safety_label_from_llm(text: str) -> str:
    """Sends text to an LLM for safety analysis."""
    prompt = f"Analyze the following chat message for safety. Classify its content as 'safe' or 'unsafe'. Respond with only the label. Message: '{text}'"
    try:
        response = model.generate_content(prompt, generation_config={"temperature": 0.0})
        return response.text.strip().lower()
    except Exception as e:
        print(f"LLM safety analysis failed: {e}")
        return "safe"

# Listener for real-time chat messages
def redis_listener():
    pubsub = r.pubsub()
    pubsub.psubscribe("chatroom:*")
    
    for message in pubsub.listen():
        if message['type'] == 'pmessage':
            channel = message['channel']
            data = json.loads(message['data'])
            
            if channel == "chatroom:broadcast":
                data["room_id"] = "ADMIN"
                sio.emit("new_message", data)
            else:
                room_id = data['room_id']
                sio.emit("new_message", data, room=room_id)

# New listener for background analysis messages
def redis_analysis_listener():
    pubsub = r.pubsub()
    pubsub.subscribe("analysis_queue")

    for message in pubsub.listen():
        if message['type'] == 'message':
            try:
                data = json.loads(message['data'])
                room_id = data.get("room_id")
                text = data.get("text")
                
                # Perform mood analysis
                mood = get_mood_from_llm(text)
                r.hincrby(f"mood_counts:{room_id}", mood, 1)

                # Perform safety analysis
                safety_label = get_safety_label_from_llm(text)
                r.hincrby(f"safety_counts:{room_id}", safety_label, 1)

                print(f"Analysis complete for message in room '{room_id}'")
            except Exception as e:
                print(f"Error processing analysis queue message: {e}")

@sio.event
def connect(sid, environ):
    print("Client connected:", sid)
    r.incr("connected_users")

@sio.event
def join(sid, data):
    room_id = data.get("room_id")
    sio.enter_room(sid, room_id)
    print(f"Client {sid} joined room {room_id}")

@sio.event
def disconnect(sid):
    print("Client disconnected:", sid)
    r.decr("connected_users")

# Start Redis listeners in separate background threads
threading.Thread(target=redis_listener, daemon=True).start()
threading.Thread(target=redis_analysis_listener, daemon=True).start()

# Start the server
if __name__ == "__main__":
    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 5000)), app)

