from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import redis
import json

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

@app.post("/chatrooms/{room_id}/messages")
async def send_message(room_id: str, request: Request):
    data = await request.json()
    message = {
        "room_id": room_id,
        "user": data.get("user"),
        "text": data.get("text")
    }
    
    # Add the chatroom to a Redis set
    r.sadd("chatrooms", room_id)
    
    # Publish the message
    r.publish(f"chatroom:{room_id}", json.dumps(message))
    return {"status": "message published"}

@app.get("/chatrooms")
def get_chatrooms():
    # Get all members of the 'chatrooms' set and filter out special channels
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
    
    # Publish to a dedicated broadcast channel
    r.publish("chatroom:broadcast", json.dumps(message))
    
    return {"status": "message published to all clients"}
