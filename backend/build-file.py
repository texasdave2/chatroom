# Create the project scaffold for a real-time chatroom backend using FastAPI, Socket.IO, Redis Pub/Sub, and Docker

import os

# Define the directory structure
project_structure = {
    "chatroom-backend": {
        "api": {
            "main.py": None,
            "redis_pub.py": None,
            "Dockerfile": None,
            "requirements.txt": None
        },
        "socket_server": {
            "main.py": None,
            "redis_sub.py": None,
            "Dockerfile": None,
            "requirements.txt": None
        },
        "docker-compose.yml": None,
        "README.md": None
    }
}

# Function to create directories and files
def create_structure(base_path, structure):
    for name, content in structure.items():
        path = os.path.join(base_path, name)
        if isinstance(content, dict):
            os.makedirs(path, exist_ok=True)
            create_structure(path, content)
        else:
            with open(path, 'w') as f:
                f.write("")

# Create the scaffold
create_structure(".", project_structure)

# Write content for API service
api_main = '''from fastapi import FastAPI, Request
import redis
import json

app = FastAPI()
r = redis.Redis(host='redis', port=6379, decode_responses=True)

@app.post("/chatrooms/{room_id}/messages")
async def send_message(room_id: str, request: Request):
    data = await request.json()
    message = {
        "room": room_id,
        "user": data.get("user"),
        "text": data.get("text")
    }
    r.publish(f"chatroom:{room_id}", json.dumps(message))
    return {"status": "message published"}
'''

api_redis_pub = '''# This file is not needed separately since Redis publishing is done in main.py
'''

api_requirements = '''fastapi
uvicorn
redis
'''

api_dockerfile = '''FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
'''

# Write content for Socket.IO server
socket_main = '''import socketio
import redis
import json

sio = socketio.Server(async_mode='threading')
app = socketio.WSGIApp(sio)

r = redis.Redis(host='redis', port=6379, decode_responses=True)
pubsub = r.pubsub()

@sio.event
def connect(sid, environ):
    print(f"Client connected: {sid}")

@sio.event
def join(sid, data):
    room = data.get("room")
    sio.enter_room(sid, room)
    print(f"{sid} joined room {room}")

def redis_listener():
    pubsub.psubscribe(**{"chatroom:*": handle_redis_message})
    pubsub.run_in_thread(sleep_time=0.001)

def handle_redis_message(message):
    if message['type'] == 'pmessage':
        data = json.loads(message['data'])
        room = data['room']
        sio.emit("new_message", data, room=room)

if __name__ == "__main__":
    redis_listener()
'''

socket_redis_sub = '''# Redis subscription is handled in main.py
'''

socket_requirements = '''python-socketio
redis
eventlet
'''

socket_dockerfile = '''FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "main.py"]
'''

# Write docker-compose file
docker_compose = '''version: "3.9"
services:
  redis:
    image: redis:7
    ports:
      - "6379:6379"

  api:
    build: ./api
    ports:
      - "8000:8000"
    depends_on:
      - redis

  socket_server:
    build: ./socket_server
    ports:
      - "5000:5000"
    depends_on:
      - redis
'''

# Write README
readme = '''# Real-Time Chatroom Backend

This project implements a real-time chatroom backend using FastAPI for REST API, Socket.IO for real-time messaging, and Redis Pub/Sub for communication between services.

## 🧱 Architecture

- `api`: FastAPI service for chatroom and message endpoints.
- `socket_server`: Socket.IO server for real-time updates.
- `redis`: Message broker for Pub/Sub communication.

## 🚀 Running Locally

Make sure you have Docker and Docker Compose installed.



