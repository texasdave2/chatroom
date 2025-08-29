from fastapi import FastAPI, Request
import redis
import json

app = FastAPI()

# Connect to Redis (host name matches the docker-compose service name)
r = redis.Redis(host='redis', port=6379, decode_responses=True)

@app.post("/chatrooms/{room_id}/messages")
async def send_message(room_id: str, request: Request):
    data = await request.json()
    message = {
        "room_id": room_id,
        "user": data.get("user"),
        "text": data.get("text")
    }
    # Publish the message to the Redis channel for the chatroom
    r.publish(f"chatroom:{room_id}", json.dumps(message))
    return {"status": "message published"}

@app.get("/")
def root():
    return {"message": "Chatroom API is running"}

