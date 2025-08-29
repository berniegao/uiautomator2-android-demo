#!/usr/bin/env python3
import socketio
import json
import time

def test_phone_control():
    print("🚀 测试通过网关控制手机...")
    
    # 创建Socket.IO客户端
    sio = socketio.Client()
    
    try:
        # 连接到网关
        print("📡 连接到网关...")
        sio.connect('http://127.0.0.1:8765')
        print("✅ 网关连接成功!")
        
        # 等待连接稳定
        time.sleep(2)
        
        # 测试1: 发送ping消息
        print("\n📱 测试1: 发送ping消息")
        ping_msg = {
            "type": "ping",
            "session": "test-session"
        }
        sio.emit('message', ping_msg)
        print("✅ Ping消息已发送")
        
        # 等待响应
        time.sleep(2)
        
        # 测试2: 发送RPC调用 - 获取设备信息
        print("\n📱 测试2: 获取设备信息")
        rpc_msg = {
            "type": "rpc.call",
            "id": "device-info-001",
            "method": "get_device_info",
            "params": {}
        }
        sio.emit('message', rpc_msg)
        print("✅ 设备信息请求已发送")
        
        # 等待响应
        time.sleep(3)
        
        # 测试3: 发送RPC调用 - 启动应用
        print("\n📱 测试3: 启动设置应用")
        rpc_msg = {
            "type": "rpc.call",
            "id": "start-app-001",
            "method": "start_app",
            "params": {
                "package_name": "com.android.settings",
                "stop": True
            }
        }
        sio.emit('message', rpc_msg)
        print("✅ 启动应用请求已发送")
        
        # 等待响应
        time.sleep(3)
        
        # 测试4: 发送RPC调用 - 执行shell命令
        print("\n📱 测试4: 执行shell命令")
        rpc_msg = {
            "type": "rpc.call",
            "id": "shell-001",
            "method": "shell",
            "params": {
                "cmd": "ls /data/local/tmp"
            }
        }
        sio.emit('message', rpc_msg)
        print("✅ Shell命令请求已发送")
        
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
    test_phone_control() 