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

@app.post("/chatrooms/{room_id}/messages")
async def send_message(room_id: str, request: Request):
    data = await request.json()
    message = {
        "room_id": room_id,
        "user": data.get("user"),
        "text": data.get("text")
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
