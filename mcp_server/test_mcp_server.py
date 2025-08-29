#!/usr/bin/env python3
"""
Test script for UIAutomator MCP Server
"""

import asyncio
import json
from uiautomator_mcp_server import UIAutomatorMCPServer


async def test_mcp_server():
    """Test the MCP server functionality"""
    print("🧪 Testing UIAutomator MCP Server...")
    
    server = UIAutomatorMCPServer()
    
    try:
        # Connect to gateway
        print("📡 Connecting to gateway...")
        await server.connect_to_gateway()
        print("✅ Connected to gateway")
        
        # Wait a bit for connection to stabilize
        await asyncio.sleep(2)
        
        # Test 1: List tools
        print("\n📋 Test 1: Listing tools...")
        tools = await server.server.get_tools()
        print(f"✅ Available tools: {tools}")
        
        # Test 2: Get device info
        print("\n📱 Test 2: Getting device info...")
        try:
            result = await server.send_rpc_call("get_device_info", {})
            print(f"✅ Device info result: {json.dumps(result, indent=2)}")
        except Exception as e:
            print(f"❌ Device info error: {e}")
        
        # Test 3: Start app
        print("\n🚀 Test 3: Starting settings app...")
        try:
            result = await server.send_rpc_call("start_app", {
                "package_name": "com.android.settings",
                "stop": True
            })
            print(f"✅ Start app result: {json.dumps(result, indent=2)}")
        except Exception as e:
            print(f"❌ Start app error: {e}")
        
        # Wait a bit before disconnecting
        await asyncio.sleep(2)
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        # Disconnect from gateway
        print("\n🔌 Disconnecting from gateway...")
        await server.disconnect_from_gateway()
        print("✅ Disconnected from gateway")


if __name__ == "__main__":
    asyncio.run(test_mcp_server()) 