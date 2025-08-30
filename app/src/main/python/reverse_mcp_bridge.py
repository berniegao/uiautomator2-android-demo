import os
import uuid
import json
import socketio
import uiautomator2 as u2
import threading
import time
import signal
import sys


class ReverseMcpBridge:
    def __init__(self, ws_url: str, token: str, adb_address: str):
        self.ws_url = ws_url
        self.token = token
        self.adb_address = adb_address
        self.device = None
        self.session_id = str(uuid.uuid4())
        self.connected = False
        self.reconnect_count = 0
        self.sio = None
        self.running = True
        self.connection_lock = threading.Lock()
        self.last_heartbeat = time.time()
        self.heartbeat_interval = 30  # Send heartbeat every 30 seconds

    def connect_device(self):
        if self.device is None:
            try:
                self.device = u2.connect(self.adb_address)
                print(f"MCP Bridge: Connected to device at {self.adb_address}")
            except Exception as e:
                print(f"MCP Bridge: Failed to connect to device: {e}")
                raise

    def send(self, msg):
        try:
            with self.connection_lock:
                if self.sio and self.connected:
                    self.sio.emit('message', msg)
                    print(f"MCP Bridge: Message sent: {msg}")
                else:
                    print(f"MCP Bridge: Cannot send message, not connected")
        except Exception as e:
            print(f"MCP Bridge: Failed to send message: {e}")
            self.connected = False

    def handle_call(self, req_id: str, method: str, params: dict):
        try:
            self.connect_device()
            d = self.device
            
            print(f"MCP Bridge: Handling call {method} with params {params}")
            
            if method == "get_device_info":
                info = d.info
                print(f"MCP Bridge: Device info retrieved: {info}")
                return {"success": True, "device_info": info}
                
            elif method == "start_app":
                pkg = params.get("package_name")
                stop = bool(params.get("stop", True))
                print(f"MCP Bridge: Starting app {pkg}, stop={stop}")
                d.app_start(pkg, stop=stop)
                return {"success": True, "message": f"App {pkg} started"}
                
            elif method == "click_text":
                text = params.get("text")
                print(f"MCP Bridge: Clicking text '{text}'")
                d(text=text).click()
                return {"success": True, "message": f"Clicked text '{text}'"}
                
            elif method == "shell":
                cmd = params.get("cmd")
                print(f"MCP Bridge: Executing shell command: {cmd}")
                res = d.shell(cmd)
                result_str = str(res)
                print(f"MCP Bridge: Shell result: {result_str}")
                return {"success": True, "result": result_str}
                
            elif method == "ping":
                return {"success": True, "message": "pong", "session": self.session_id}
                
            else:
                print(f"MCP Bridge: Unknown method: {method}")
                return {"success": False, "error": f"Unknown method: {method}"}
                
        except Exception as e:
            print(f"MCP Bridge: Error handling call {method}: {e}")
            return {"success": False, "error": str(e)}

    def handle_incoming_message(self, data):
        try:
            if isinstance(data, str):
                msg = json.loads(data)
            else:
                msg = data
                
            print(f"MCP Bridge: Received message: {msg}")
            
            # Update last heartbeat time
            self.last_heartbeat = time.time()
            
            if msg.get("type") == "rpc.call":
                req_id = msg.get("id")
                method = msg.get("method")
                params = msg.get("params") or {}
                
                print(f"MCP Bridge: Processing RPC call {req_id}: {method}")
                result = self.handle_call(req_id, method, params)
                
                response = {"type": "rpc.result", "id": req_id, "result": result}
                self.send(response)
            elif msg.get("type") == "ping":
                # Respond to ping with pong
                pong_msg = {"type": "pong", "session": self.session_id, "timestamp": time.time()}
                self.send(pong_msg)
                print(f"MCP Bridge: Responded to ping with pong")
            elif msg.get("type") == "heartbeat":
                # Respond to heartbeat
                heartbeat_response = {"type": "heartbeat_ack", "session": self.session_id, "timestamp": time.time()}
                self.send(heartbeat_response)
                print(f"MCP Bridge: Responded to heartbeat")
                print(f"MCP Bridge: Sent response: {response}")
                
            elif msg.get("type") == "ping":
                pong_msg = {"type": "pong", "session": self.session_id}
                self.send(pong_msg)
                print(f"MCP Bridge: Sent pong response")
                
        except json.JSONDecodeError as e:
            print(f"MCP Bridge: Failed to parse message: {e}")
        except Exception as e:
            print(f"MCP Bridge: Error processing message: {e}")

    def run(self):
        print(f"MCP Bridge: Starting connection to {self.ws_url}")
        print(f"MCP Bridge: Session ID: {self.session_id}")
        print(f"MCP Bridge: Token: {self.token}")
        
        # Create Socket.IO client
        self.sio = socketio.Client()
        
        @self.sio.event
        def connect():
            self.connected = True
            self.reconnect_count = 0
            print(f"MCP Bridge: Successfully connected to gateway!")
            
            # Send hello message
            hello_msg = {"type": "hello", "session": self.session_id, "device": self.adb_address}
            self.send(hello_msg)
            print(f"MCP Bridge: Sent hello message: {hello_msg}")
        
        @self.sio.event
        def disconnect():
            self.connected = False
            print(f"MCP Bridge: Disconnected from gateway")
        
        @self.sio.event
        def message(data):
            print(f"MCP Bridge: Received message: {data}")
            self.handle_incoming_message(data)
        
        while True:
            try:
                print(f"MCP Bridge: Attempting to connect to gateway...")
                
                # Force disconnect if still connected
                if self.sio.connected:
                    print(f"MCP Bridge: Force disconnecting existing connection...")
                    self.sio.disconnect()
                    self.connected = False
                    time.sleep(1)
                
                # Create new Socket.IO client for each connection attempt
                if self.sio:
                    self.sio.disconnect()
                self.sio = socketio.Client()
                
                # Re-register event handlers
                @self.sio.event
                def connect():
                    self.connected = True
                    self.reconnect_count = 0
                    print(f"MCP Bridge: Successfully connected to gateway!")
                    
                    # Send hello message
                    hello_msg = {"type": "hello", "session": self.session_id, "device": self.adb_address}
                    self.send(hello_msg)
                    print(f"MCP Bridge: Sent hello message: {hello_msg}")
                
                @self.sio.event
                def disconnect():
                    self.connected = False
                    print(f"MCP Bridge: Disconnected from gateway")
                
                @self.sio.event
                def message(data):
                    print(f"MCP Bridge: Received message: {data}")
                    self.handle_incoming_message(data)
                
                # Attempt connection
                self.sio.connect(
                    self.ws_url, 
                    headers={"Authorization": f"Bearer {self.token}", "X-Device-Id": self.session_id},
                    wait_timeout=10  # 10 second timeout
                )
                
                # Keep connection alive with heartbeat
                while self.connected and self.running:
                    current_time = time.time()
                    
                    # Send heartbeat if needed
                    if current_time - self.last_heartbeat >= self.heartbeat_interval:
                        try:
                            heartbeat_msg = {"type": "heartbeat", "session": self.session_id, "timestamp": current_time}
                            self.send(heartbeat_msg)
                            print(f"MCP Bridge: Sent heartbeat at {current_time}")
                        except Exception as e:
                            print(f"MCP Bridge: Failed to send heartbeat: {e}")
                            self.connected = False
                            break
                    
                    # Check for stop signal every second
                    for _ in range(10):  # Check every 100ms for 1 second total
                        if not self.running:
                            break
                        time.sleep(0.1)
                    
                    if not self.running:
                        break
                    
            except Exception as e:
                self.connected = False
                print(f"MCP Bridge: Connection error: {e}")
                print(f"MCP Bridge: Error type: {type(e).__name__}")
                
                # Force cleanup
                try:
                    if self.sio and self.sio.connected:
                        self.sio.disconnect()
                except:
                    pass
            
            # Wait before reconnecting
            if not self.running:
                print("MCP Bridge: Service stopped, exiting reconnection loop")
                break
                
            self.reconnect_count += 1
            wait_time = min(3 * self.reconnect_count, 30)  # Exponential backoff, max 30s
            print(f"MCP Bridge: Reconnecting in {wait_time} seconds... (attempt {self.reconnect_count})")
            
            # Wait with periodic checks for stop signal
            for _ in range(wait_time):
                if not self.running:
                    break
                time.sleep(1)
                    
    def stop(self):
        """Stop the bridge service"""
        print("MCP Bridge: Stopping service...")
        self.running = False
        self.connected = False
        
        # Disconnect socket
        try:
            if self.sio and self.sio.connected:
                self.sio.disconnect()
        except:
            pass
            
        print("MCP Bridge: Service stopped")


def start_reverse_mcp_from_env(adb_address: str):
    ws_url = os.environ.get("MCP_GATEWAY_WS_URL")
    token = os.environ.get("MCP_GATEWAY_TOKEN")
    
    if not ws_url or not token:
        print("MCP Bridge: Missing environment variables, skipping MCP bridge startup")
        print(f"MCP Bridge: MCP_GATEWAY_WS_URL={ws_url}")
        print(f"MCP Bridge: MCP_GATEWAY_TOKEN={token}")
        return
    
    print(f"MCP Bridge: Starting with URL={ws_url}, token={token[:8]}..., device={adb_address}")
    
    try:
        bridge = ReverseMcpBridge(ws_url, token, adb_address)
        # Run in a separate thread to avoid blocking
        bridge_thread = threading.Thread(target=bridge.run, daemon=True)
        bridge_thread.start()
        print(f"MCP Bridge: Started in background thread")
    except Exception as e:
        print(f"MCP Bridge: Fatal error: {e}")
        # Don't re-raise - let the main app continue running

