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

@app.post("/chatrooms/{room_id}/messages")
async def send_message(room_id: str, request: Request):
    data = await request.json()
    message = {
        "room_id": room_id,
        "user": data.get("user"),
        "text": data.get("text")
    }
    r.publish(f"chatroom:{room_id}", json.dumps(message))
    return {"status": "message published"}

