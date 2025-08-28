#!/usr/bin/env python3
import socketio
import eventlet

# Create a Socket.IO server
sio = socketio.Server(cors_allowed_origins="*")
app = socketio.WSGIApp(sio)

@sio.event
def connect(sid, environ):
    print(f"Client connected: {sid}")

@sio.event
def disconnect(sid):
    print(f"Client disconnected: {sid}")

@sio.event
def message(sid, data):
    print(f"Received message from {sid}: {data}")
    sio.emit("response", f"Echo: {data}", room=sid)

if __name__ == "__main__":
    print("Starting Socket.IO server on http://0.0.0.0:8080")
    eventlet.wsgi.server(eventlet.listen(("0.0.0.0", 8080)), app)
