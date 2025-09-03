from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import redis
import json
import os
import google.generativeai as genai

# Configure the LLM
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

app = FastAPI()
r = redis.Redis(host='redis', port=6379, decode_responses=True)

# Serve static files from /static
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve index.html at root
@app.get("/")
def serve_frontend():
    return FileResponse("static/index.html")

# Endpoint to serve the admin page
@app.get("/admin")
def serve_admin_page():
    return FileResponse("static/admin.html")

# New endpoint for admin metrics
@app.get("/admin/metrics")
def get_admin_metrics():
    # Get total number of unique chatrooms from the Redis set
    total_chatrooms = r.scard("chatrooms")
    # Get total number of connected users from the Redis counter
    total_connected_users = r.get("connected_users")

    # Handle the case where the counter might not exist yet
    if total_connected_users is None:
        total_connected_users = 0
    else:
        total_connected_users = int(total_connected_users)

    return {
        "chatrooms": total_chatrooms,
        "connected_users": total_connected_users
    }

# New endpoint for mood analysis data
@app.get("/admin/mood_analysis")
def get_mood_analysis():
    mood_data = {}
    # Get all keys that start with "mood_counts:"
    mood_keys = r.keys("mood_counts:*")
    
    for key in mood_keys:
        room_id = key.split(":")[1]
        counts = r.hgetall(key)
        mood_data[room_id] = {
            "happy": int(counts.get("happy", 0)),
            "sad": int(counts.get("sad", 0)),
            "neutral": int(counts.get("neutral", 0)),
        }
    return mood_data

# New endpoint for safety analysis data
@app.get("/admin/safety_analysis")
def get_safety_analysis():
    safety_data = {}
    # Get all keys that start with "safety_counts:"
    safety_keys = r.keys("safety_counts:*")
    
    for key in safety_keys:
        room_id = key.split(":")[1]
        counts = r.hgetall(key)
        safety_data[room_id] = {
            "safe": int(counts.get("safe", 0)),
            "unsafe": int(counts.get("unsafe", 0)),
        }
    return safety_data

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
    # New prompt for safety analysis.
    prompt = f"Analyze the following chat message for safety. Classify its content as 'safe' or 'unsafe'. Respond with only the label. Message: '{text}'"
    try:
        response = model.generate_content(prompt, generation_config={"temperature": 0.0})
        return response.text.strip().lower()
    except Exception as e:
        print(f"LLM safety analysis failed: {e}")
        return "safe"

@app.post("/chatrooms/{room_id}/messages")
async def send_message(room_id: str, request: Request):
    data = await request.json()
    text = data.get("text")
    user = data.get("user")
    
    # Perform mood analysis
    mood = get_mood_from_llm(text)
    r.hincrby(f"mood_counts:{room_id}", mood, 1)

    # Perform safety analysis
    safety_label = get_safety_label_from_llm(text)
    r.hincrby(f"safety_counts:{room_id}", safety_label, 1)

    message = {
        "room_id": room_id,
        "user": user,
        "text": text,
        "mood": mood,
        "safety": safety_label # You can also send the safety label to the frontend
    }

    r.sadd("chatrooms", room_id)
    r.publish(f"chatroom:{room_id}", json.dumps(message))
    return {"status": "message published"}

@app.get("/chatrooms")
def get_chatrooms():
    chatrooms = [room for room in r.smembers("chatrooms") if room not in ["all", "broadcast"]]
    return {"chatrooms": chatrooms}

@app.post("/admin/broadcast")
async def send_admin_broadcast(request: Request):
    data = await request.json()
    user = data.get("user")
    text = data.get("text")
    
    message = {
        "user": user,
        "text": text
    }
    r.publish("chatroom:broadcast", json.dumps(message))
    return {"status": "message published to all clients"}
