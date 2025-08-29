#!/usr/bin/env python3
import socketio
import time

def test_gateway_events():
    print("🧪 测试网关的Socket.IO事件处理...")
    
    # 创建Socket.IO客户端
    sio = socketio.Client()
    
    try:
        # 连接到网关
        print("📡 连接到网关...")
        sio.connect('http://127.0.0.1:8765')
        print("✅ 网关连接成功!")
        
        # 等待连接稳定
        time.sleep(2)
        
        # 发送一个简单的消息
        print("📤 发送测试消息...")
        test_msg = {"type": "test", "data": "hello"}
        sio.emit('message', test_msg)
        print("✅ 测试消息已发送")
        
        # 等待响应
        time.sleep(3)
        
        # 断开连接
        sio.disconnect()
        print("✅ 断开连接")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_gateway_events() 