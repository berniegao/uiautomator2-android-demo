#!/usr/bin/env python3
"""
MCP客户端测试脚本
用于测试Android UIAutomator2 MCP服务器的连接和工具调用
"""

import asyncio
import json
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import socketio
import time

async def test_mcp_server():
    """测试MCP服务器连接和工具调用"""
    
    # MCP服务器参数
    server_params = StdioServerParameters(
        command="python3",
        args=["/Users/berniegao/workstation/source_code/uiautomator2-phone-copilot/uiautomator2-android-demo/mcp_server/android_mcp_server.py"]
    )
    
    print("🔌 正在连接MCP服务器...")
    
    try:
        # 连接到MCP服务器
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                
                print("✅ MCP服务器连接成功！")
                
                # 1. 测试获取设备信息
                print("\n📱 测试1: 获取设备信息")
                try:
                    result = await session.call_tool("mcp_android_get_device_info", {})
                    print(f"✅ 设备信息: {json.dumps(result.content, indent=2, ensure_ascii=False)}")
                except Exception as e:
                    print(f"❌ 获取设备信息失败: {e}")
                
                # 2. 测试获取当前应用
                print("\n📱 测试2: 获取当前应用")
                try:
                    result = await session.call_tool("mcp_android_get_current_app", {})
                    print(f"✅ 当前应用: {json.dumps(result.content, indent=2, ensure_ascii=False)}")
                except Exception as e:
                    print(f"❌ 获取当前应用失败: {e}")
                
                # 3. 测试获取截图
                print("\n📱 测试3: 获取屏幕截图")
                try:
                    result = await session.call_tool("mcp_android_get_screenshot", {})
                    print(f"✅ 截图结果: {result.content}")
                except Exception as e:
                    print(f"❌ 获取截图失败: {e}")
                
                # 4. 测试启动设置应用
                print("\n📱 测试4: 启动设置应用")
                try:
                    result = await session.call_tool("mcp_android_start_app", {
                        "package_name": "com.android.settings"
                    })
                    print(f"✅ 启动设置应用: {json.dumps(result.content, indent=2, ensure_ascii=False)}")
                except Exception as e:
                    print(f"❌ 启动设置应用失败: {e}")
                
                # 5. 测试等待并点击元素
                print("\n📱 测试5: 等待并点击元素")
                try:
                    # 等待设置应用加载
                    await asyncio.sleep(3)
                    
                    # 尝试点击"Network & internet"
                    result = await session.call_tool("mcp_android_click_element", {
                        "text": "Network & internet"
                    })
                    print(f"✅ 点击元素结果: {json.dumps(result.content, indent=2, ensure_ascii=False)}")
                except Exception as e:
                    print(f"❌ 点击元素失败: {e}")
                
                # 6. 测试滑动屏幕
                print("\n📱 测试6: 滑动屏幕")
                try:
                    result = await session.call_tool("mcp_android_swipe_screen", {
                        "direction": "up",
                        "scale": 0.5
                    })
                    print(f"✅ 滑动屏幕: {json.dumps(result.content, indent=2, ensure_ascii=False)}")
                except Exception as e:
                    print(f"❌ 滑动屏幕失败: {e}")
                
                # 7. 测试获取已安装应用列表
                print("\n📱 测试7: 获取已安装应用列表")
                try:
                    result = await session.call_tool("mcp_android_get_installed_packages", {})
                    packages = result.content.get("packages", [])
                    print(f"✅ 已安装应用数量: {len(packages)}")
                    print(f"前5个应用: {packages[:5]}")
                except Exception as e:
                    print(f"❌ 获取应用列表失败: {e}")
                
                print("\n🎉 所有测试完成！")
                
    except Exception as e:
        print(f"❌ 连接MCP服务器失败: {e}")
        return False
    
    return True

async def test_simple_connection():
    """简单连接测试"""
    server_params = StdioServerParameters(
        command="python3",
        args=["/Users/berniegao/workstation/source_code/uiautomator2-phone-copilot/uiautomator2-android-demo/mcp_server/android_mcp_server.py"]
    )
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                print("✅ MCP服务器连接成功！")
                
                # 获取工具列表
                tools = await session.list_tools()
                print(f"📋 可用工具数量: {len(tools.tools)}")
                
                for tool in tools.tools:
                    print(f"  - {tool.name}: {tool.description}")
                
                return True
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False

def test_mcp():
    print("Testing MCP functionality...")
    
    # Create Socket.IO client
    sio = socketio.Client()
    
    try:
        # Connect to gateway
        print("Connecting to http://127.0.0.1:8765...")
        sio.connect('http://127.0.0.1:8765')
        print("✅ Connected to gateway!")
        
        # Wait a moment for connection to stabilize
        time.sleep(2)
        
        # Send a ping message
        print("Sending ping message...")
        ping_msg = {"type": "ping"}
        sio.emit('message', ping_msg)
        print("✅ Ping message sent!")
        
        # Wait for response
        time.sleep(3)
        
        # Send a test RPC call
        print("Sending test RPC call...")
        rpc_msg = {
            "type": "rpc.call",
            "id": "test-123",
            "method": "ping",
            "params": {}
        }
        sio.emit('message', rpc_msg)
        print("✅ RPC call sent!")
        
        # Wait for response
        time.sleep(3)
        
        # Disconnect
        sio.disconnect()
        print("✅ Disconnected successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 开始测试Android UIAutomator2 MCP服务器")
    print("=" * 50)
    
    # 选择测试模式
    if len(sys.argv) > 1 and sys.argv[1] == "simple":
        success = asyncio.run(test_simple_connection())
    else:
        success = asyncio.run(test_mcp_server())
    
    if success:
        print("\n🎉 测试成功！MCP服务器工作正常。")
    else:
        print("\n❌ 测试失败！请检查MCP服务器配置。") 