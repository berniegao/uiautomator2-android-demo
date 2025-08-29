#!/usr/bin/env python3
"""
Test script for UIAutomator SSE MCP Server using MCP client
"""

import asyncio
import json
from mcp.client.sse import sse_client
from mcp.shared.message import SessionMessage
from mcp.types import ListToolsRequest, CallToolRequest, InitializeRequest, CallToolRequestParams, InitializedNotification


async def test_sse_server():
    """Test the SSE MCP server using MCP client"""
    print("🧪 Testing UIAutomator SSE MCP Server...")
    
    # SSE server URL
    sse_url = "http://127.0.0.1:8766/mcp"
    
    try:
        # Connect to SSE server using MCP client
        print("📡 Connecting to SSE server...")
        async with sse_client(sse_url) as (read, write):
            print("✅ Connected to SSE server")
            
            # Initialize session first
            print("\n🔧 Initializing session...")
            try:
                init_request = InitializeRequest(
                    id=0,
                    method="initialize",
                    jsonrpc="2.0",
                    params={
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "clientInfo": {
                            "name": "test-client",
                            "version": "1.0.0"
                        }
                    }
                )
                session_message = SessionMessage(message=init_request)
                await write.send(session_message)
                response = await read.receive()
                print(f"✅ Initialize response: {response}")
                
                # Send initialized notification
                print("🔄 Sending initialized notification...")
                initialized_notification = InitializedNotification(
                    method="notifications/initialized",
                    jsonrpc="2.0",
                    params={}
                )
                session_message = SessionMessage(message=initialized_notification)
                await write.send(session_message)
                print("✅ Initialized notification sent")
                
            except Exception as e:
                print(f"❌ Initialize error: {e}")
                import traceback
                traceback.print_exc()
                return
            
            # Test 1: List tools
            print("\n📋 Test 1: Listing tools...")
            try:
                # Create proper MCP request
                tools_request = ListToolsRequest(id=1, method="tools/list", jsonrpc="2.0", params=None)
                session_message = SessionMessage(message=tools_request)
                await write.send(session_message)
                response = await read.receive()
                print(f"✅ Tools response: {response}")
            except Exception as e:
                print(f"❌ List tools error: {e}")
                import traceback
                traceback.print_exc()
            
            # Test 2: Get device info
            print("\n📱 Test 2: Getting device info...")
            try:
                device_info_request = CallToolRequest(
                    id=2,
                    method="tools/call",
                    jsonrpc="2.0",
                    params=CallToolRequestParams(
                        name="get_device_info",
                        arguments={}
                    )
                )
                session_message = SessionMessage(message=device_info_request)
                await write.send(session_message)
                response = await read.receive()
                print(f"✅ Device info response: {response}")
            except Exception as e:
                print(f"❌ Device info error: {e}")
            
            # Test 3: Start app
            print("\n🚀 Test 3: Starting settings app...")
            try:
                start_app_request = CallToolRequest(
                    id=3,
                    method="tools/call",
                    jsonrpc="2.0",
                    params=CallToolRequestParams(
                        name="start_app",
                        arguments={
                            "package_name": "com.android.settings",
                            "stop": True
                        }
                    )
                )
                session_message = SessionMessage(message=start_app_request)
                await write.send(session_message)
                response = await read.receive()
                print(f"✅ Start app response: {response}")
            except Exception as e:
                print(f"❌ Start app error: {e}")
            
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(test_sse_server()) 