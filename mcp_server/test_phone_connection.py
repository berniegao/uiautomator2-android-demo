#!/usr/bin/env python3
import socketio
import time

def test_connection():
    print("Testing Socket.IO connection to gateway...")
    
    # Create Socket.IO client
    sio = socketio.Client()
    
    try:
        # Connect to gateway
        print("Connecting to ws://127.0.0.1:8765...")
        sio.connect('http://127.0.0.1:8765')
        print("✅ Socket.IO connection successful!")
        
        # Send a test message
        print("Sending test message...")
        sio.emit('message', {'type': 'test', 'data': 'Hello from phone!'})
        print("✅ Test message sent!")
        
        # Wait a moment
        time.sleep(1)
        
        # Disconnect
        sio.disconnect()
        print("✅ Disconnected successfully!")
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_connection() 