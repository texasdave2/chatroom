#! /bin/bash
curl -X POST http://localhost:8100/chatrooms/room1/messages \
     -H "Content-Type: application/json" \
     -d '{"user": "Alice", "text": "Hello everyone!"}'

