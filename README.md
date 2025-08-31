Real-Time Chatroom with AI Analysis

This project is a real-time chatroom application built with Python and FastAPI, featuring an admin panel for live analytics powered by a large language model (LLM). It provides a complete, multi-service solution for a modern, interactive chat platform.

The application is designed for easy deployment using Docker Compose, making it simple to set up and run the entire stack.

Key Technologies

FastAPI: The web framework for the main API backend, serving the static files and handling API requests.

Socket.IO: The library used for real-time, bidirectional communication between the clients and the server.

Redis: Serves as the central data store for pub/sub messaging, user counts, and chatroom analysis metrics.

Google Gemini (LLM): Integrated via API to perform real-time sentiment and safety analysis on chat messages.

Docker Compose: Used to orchestrate and deploy the multi-service application (API, Socket.IO server, and Redis).

Features

Real-Time Messaging: Users can join and participate in various chatrooms with messages appearing instantly.

Persistent Chatrooms: Chatrooms are stored in Redis, allowing them to persist even after all users have left.

Live Admin Panel: A dedicated admin interface that provides real-time insights into the chat network.

Live Metrics: Displays the total number of chatrooms and the total number of connected users.

Mood Analysis: Analyzes each message for sentiment and provides a count of "happy," "sad," and "neutral" messages per chatroom.

Safety Analysis: Classifies messages as "safe" or "unsafe," providing a crucial moderation tool.

Admin Broadcast: Allows an administrator to send a message to every chatroom simultaneously.

Deployment

To deploy this application, you will need to have Docker and Docker Compose installed.

Get an API Key: Obtain a Google API key from Google AI Studio. This key is required for the LLM analysis.

Create a .env file: In the root directory of the project, create a .env file with the following content:GOOGLE_API_KEY=your_api_key_here

Run with Docker Compose: Execute the following command in your terminal. This will build the images and start all the services (API, Socket.IO server, and Redis) in the background.

docker compose up -d --build

Usage

Once the application is running, you can access the following endpoints in your browser:

User Interface: Navigate to http://localhost:8100 to access the main chatroom. Enter a username and a chatroom name to start.

Admin Panel: Navigate to http://localhost:8100/admin to access the administrator dashboard. Here you can see live metrics and send broadcast messages.

Project Structure.

├── backend/
│   ├── api/
│   │   ├── Dockerfile
│   │   ├── main.py                # FastAPI server, API endpoints, LLM analysis
│   │   ├── requirements.txt
│   │   └── static/
│   │       ├── admin.html         # Admin dashboard HTML
│   │       └── index.html         # User chatroom HTML
│   ├── docker-compose.yml       # Defines the multi-container application
│   ├── socket_server/
│   │   ├── Dockerfile
│   │   ├── main.py              # Socket.IO server, Redis pub/sub listener
│   │   └── requirements.txt
│   └── test/
│       └── hello.sh
└── README.md

