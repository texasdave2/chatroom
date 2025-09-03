from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import redis
import json
import os
import google.generativeai as genai
import textwrap

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

def get_assistant_response_from_llm(prompt: str) -> str:
    """Sends a prompt to the LLM and returns a free-form text response."""
    try:
        response = model.generate_content(prompt)
        # Use textwrap.dedent to remove leading whitespace from the response
        return textwrap.dedent(response.text.strip())
    except Exception as e:
        print(f"LLM generation failed: {e}")
        return "Sorry, I am unable to generate a response right now."

@app.post("/chatrooms/{room_id}/messages")
async def send_message(room_id: str, request: Request):
    data = await request.json()
    text = data.get("text")
    user = data.get("user")
    
    # Check if the message is for the AI assistant
    if text.startswith("@assistant"):
        user_prompt = text.replace("@assistant", "", 1).strip()
        assistant_response = get_assistant_response_from_llm(user_prompt)
        
        # Publish the assistant's response to the chatroom
        assistant_message = {
            "room_id": room_id,
            "user": "Assistant",
            "text": assistant_response
        }
        r.publish(f"chatroom:{room_id}", json.dumps(assistant_message))

    # Existing logic for background analysis
    analysis_data = {
        "room_id": room_id,
        "text": text
    }
    r.publish("analysis_queue", json.dumps(analysis_data))

    # Existing logic for the user's message
    message = {
        "room_id": room_id,
        "user": user,
        "text": text
    }
    r.publish(f"chatroom:{room_id}", json.dumps(message))

    r.sadd("chatrooms", room_id)
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

