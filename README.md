# 🗨️ Real-Time Chatroom Backend

This project implements a scalable real-time chatroom backend using **FastAPI**, **Socket.IO**, **Redis Pub/Sub**, and **Docker**. It demonstrates a microservice architecture where the REST API and real-time server are decoupled and communicate via Redis.

---

## 🧱 Architecture Overview

- **API Service** (`api/`): Handles REST endpoints for sending messages.
- **Socket.IO Server** (`socket_server/`): Manages real-time communication with clients.
- **Redis**: Acts as a message broker using Pub/Sub.
- **Docker Compose**: Orchestrates all services for local development.

---

## 🚀 Getting Started

### Prerequisites
- Docker
- Docker Compose

### Run the Project

```bash
docker-compose up --build

