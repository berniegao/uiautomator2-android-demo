#!/usr/bin/env python3
"""
Minimal reverse-connection MCP gateway (Socket.IO).

Phone app connects OUTBOUND to this server with headers:
  Authorization: Bearer <TOKEN>
  X-Device-Id: <UUID>

You can then type simple commands in this process to call the phone:
  call <method> <json_params>
Examples:
  call get_device_info {}
  call start_app {"package_name":"com.android.settings","stop":true}
  call click_text {"text":"Network & internet"}
  call shell {"cmd":"pm list packages -3"}
"""

import os
import sys
import uuid
import json
import threading
import logging
from typing import Dict

import socketio
import eventlet


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('gateway.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

HOST = "0.0.0.0"  # Force listen on all interfaces
PORT = int(os.environ.get("GATEWAY_PORT", "8765"))
TOKEN = os.environ.get("GATEWAY_TOKEN", "devtoken")


class Gateway:
    def __init__(self):
        self.device_connections: Dict[str, str] = {}  # device_id -> sid
        self.pending: Dict[str, threading.Event] = {}
        self.results: Dict[str, dict] = {}
        
        logger.info("Gateway: Initializing Socket.IO server...")
        
        # Create Socket.IO server
        self.sio = socketio.Server(cors_allowed_origins='*')
        self.app = socketio.WSGIApp(self.sio)
        
        logger.info("Gateway: Registering Socket.IO event handlers...")
        
        # Register Socket.IO events
        self.sio.on('connect', self.on_connect)
        self.sio.on('disconnect', self.on_disconnect)
        self.sio.on('message', self.on_message)
        self.sio.on('rpc_result', self.on_rpc_result)
        self.sio.on('rpc_error', self.on_rpc_error)
        
        logger.info("Gateway: Socket.IO event handlers registered successfully")

    def on_connect(self, sid, environ):
        logger.info(f"Gateway: New connection from {sid}")
        logger.debug(f"Gateway: Environment: {environ}")
        device_id = str(uuid.uuid4())
        self.device_connections[device_id] = sid
        logger.info(f"Gateway: Device connected: {device_id} (sid: {sid})")
        logger.info(f"Gateway: Total connections: {len(self.device_connections)}")

    def on_disconnect(self, sid):
        logger.info(f"Gateway: Client disconnected: {sid}")
        # Find and remove device
        for device_id, device_sid in list(self.device_connections.items()):
            if device_sid == sid:
                self.device_connections.pop(device_id, None)
                logger.info(f"Gateway: Device disconnected: {device_id}")
                break
        logger.info(f"Gateway: Remaining connections: {len(self.device_connections)}")

    def on_message(self, sid, data):
        logger.info(f"Gateway: Received message from {sid}: {data}")
        logger.debug(f"Gateway: Message type: {type(data)}")
        # Handle different message types
        if isinstance(data, dict):
            msg_type = data.get("type")
            logger.debug(f"Gateway: Message type: {msg_type}")
            if msg_type == "hello":
                logger.info(f"Gateway: hello from {sid}: {data}")
            elif msg_type == "ping":
                logger.debug(f"Gateway: ping from {sid}")
                # Send pong response
                pong_msg = {"type": "pong", "session": data.get("session", "unknown")}
                self.sio.emit('message', pong_msg, room=sid)
                logger.debug(f"Gateway: Sent pong response to {sid}")
            elif msg_type == "rpc.call":
                logger.info(f"Gateway: RPC call from {sid}: {data}")
                # Forward to device
                req_id = data.get("id")
                method = data.get("method")
                params = data.get("params", {})
                logger.info(f"Gateway: Forwarding RPC call {req_id}: {method}")
                
                # Find the device that sent this RPC call
                device_sid = None
                for device_id, device_sid in self.device_connections.items():
                    if device_sid == sid:  # Check if this is the device
                        break
                
                if device_sid:
                    # Forward RPC call to the device
                    logger.info(f"Gateway: Forwarding RPC call to device {device_sid}")
                    self.sio.emit('message', data, room=device_sid)
                else:
                    # No device found, send error response
                    response = {
                        "type": "rpc.error",
                        "id": req_id,
                        "error": "No device connected"
                    }
                    self.sio.emit('message', response, room=sid)
                    logger.warning(f"Gateway: No device found, sent error response")
            elif msg_type == "rpc.result":
                logger.info(f"Gateway: RPC result from {sid}: {data}")
                req_id = data.get("id")
                if req_id in self.pending:
                    self.results[req_id] = data
                    self.pending[req_id].set()
            elif msg_type == "rpc.error":
                logger.warning(f"Gateway: RPC error from {sid}: {data}")
                req_id = data.get("id")
                if req_id in self.pending:
                    self.results[req_id] = data
                    self.pending[req_id].set()

    def on_rpc_result(self, sid, data):
        req_id = data.get("id")
        logger.info(f"Gateway: RPC result from {sid}, req_id: {req_id}")
        if req_id in self.pending:
            self.results[req_id] = data
            self.pending[req_id].set()

    def on_rpc_error(self, sid, data):
        req_id = data.get("id")
        logger.warning(f"Gateway: RPC error from {sid}, req_id: {req_id}")
        if req_id in self.pending:
            self.results[req_id] = data
            self.pending[req_id].set()

    def call(self, device_id: str, method: str, params: dict, timeout: float = 30.0):
        sid = self.device_connections.get(device_id)
        if not sid:
            raise RuntimeError(f"device {device_id} not connected")
        
        req_id = str(uuid.uuid4())
        event = threading.Event()
        self.pending[req_id] = event
        
        # Send RPC call
        message = {
            "type": "rpc.call",
            "id": req_id,
            "method": method,
            "params": params,
        }
        self.sio.emit('rpc_call', message, room=sid)
        
        try:
            if event.wait(timeout):
                result = self.results.pop(req_id, None)
                if result:
                    return result
                else:
                    raise RuntimeError("No result received")
            else:
                raise RuntimeError("RPC call timeout")
        finally:
            self.pending.pop(req_id, None)


def repl(gw: Gateway):
    logger.info("Commands:\n  devices\n  use <deviceId>\n  call <method> <json_params>\n  quit")
    current = None
    while True:
        try:
            line = input("> ")
        except (EOFError, KeyboardInterrupt):
            break
        if not line:
            continue
        line = line.strip()
        if line in ("quit", "exit"):
            break
        if line == "devices":
            logger.info("Connected:", list(gw.device_connections.keys()))
            continue
        if line.startswith("use "):
            current = line.split(" ", 1)[1]
            logger.info("Using:", current)
            continue
        if line.startswith("call "):
            if not current:
                logger.warning("Select device: use <deviceId>")
                continue
            try:
                _, method, json_str = line.split(" ", 2)
                params = json.loads(json_str)
            except Exception as e:
                logger.error("Bad command:", e)
                continue
            try:
                resp = gw.call(current, method, params)
                logger.info("Response:", resp)
            except Exception as e:
                logger.error("Error:", e)
            continue
        logger.warning("Unknown command")


def main():
    import sys
    import os
    
    logger.info("Gateway: Starting main function...")
    
    try:
        logger.info("Gateway: Creating Gateway instance...")
        gw = Gateway()
        logger.info("Gateway: Gateway instance created successfully")
        logger.info(f"Gateway: Device connections: {len(gw.device_connections)}")
        logger.info(f"Gateway: Socket.IO server: {gw.sio}")
        logger.info(f"Gateway: WSGI app: {gw.app}")
    except Exception as e:
        logger.error(f"Gateway: Error creating Gateway instance: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Force listen on all interfaces
    host = "0.0.0.0"
    port = 8765
    
    logger.info(f"Gateway: Starting Socket.IO server on {host}:{port}")
    logger.info(f"Gateway: This will listen on ALL network interfaces")
    
    # Start Socket.IO server
    logger.info(f"Gateway listening on http://{host}:{port}  (TOKEN={TOKEN})")
    logger.info(f"Gateway: Server should be accessible from external networks")
    
    # Start server using eventlet spawn
    logger.info(f"Gateway: Starting eventlet server on {host}:{port}")
    try:
        # Start server in background
        eventlet.spawn(eventlet.wsgi.server, eventlet.listen((host, port)), gw.app)
        logger.info("Gateway: Server started successfully")
    except Exception as e:
        logger.error(f"Gateway: Error starting server: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Keep server running
    try:
        while True:
            eventlet.sleep(1)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()

