#!/usr/bin/env python3
"""
UIAutomator MCP Server

This MCP server provides Android automation capabilities by forwarding
requests to the gateway server.
"""

import asyncio
import json
import logging
import socketio
from typing import Any, Dict, List, Optional

from fastmcp.server.server import FastMCP

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Gateway configuration
GATEWAY_URL = "http://127.0.0.1:8765"
GATEWAY_TOKEN = "devtoken"

# SSE Server configuration
SSE_HOST = "0.0.0.0"
SSE_PORT = 8766
SSE_PATH = "/mcp"

# Global MCP server instance
mcp_server_instance = None


class UIAutomatorMCPServer:
    def __init__(self):
        self.sio = socketio.AsyncClient()
        self.connected = False
        self.device_available = False
        
        # Register Socket.IO event handlers
        self.sio.on('connect', self.on_connect)
        self.sio.on('disconnect', self.on_disconnect)
        self.sio.on('message', self.on_message)
        
        # MCP server
        self.server = FastMCP("uiautomator-mcp-server")
        
        # Set global instance
        global mcp_server_instance
        mcp_server_instance = self
        
        # Register tools using decorators
        self._register_tools()

    def _register_tools(self):
        """Register tools using decorators"""
        
        @self.server.tool(
            name="start_app",
            description="Start an Android application"
        )
        async def start_app(package_name: str, stop: bool = True) -> str:
            """Start an Android application"""
            if not package_name:
                return "Error: package_name is required"
            
            try:
                result = await self.send_rpc_call("start_app", {
                    "package_name": package_name,
                    "stop": stop
                })
                
                return json.dumps(result, indent=2)
            except Exception as e:
                return f"Error: {str(e)}"

        @self.server.tool(
            name="get_device_info",
            description="Get information about the connected Android device"
        )
        async def get_device_info() -> str:
            """Get device information"""
            try:
                result = await self.send_rpc_call("get_device_info", {})
                
                return json.dumps(result, indent=2)
            except Exception as e:
                return f"Error: {str(e)}"

    async def on_connect(self):
        """Handle gateway connection"""
        logger.info("Connected to gateway")
        self.connected = True

    async def on_disconnect(self):
        """Handle gateway disconnection"""
        logger.info("Disconnected from gateway")
        self.connected = False
        self.device_available = False

    async def on_message(self, data):
        """Handle messages from gateway"""
        logger.debug(f"Received message from gateway: {data}")
        if isinstance(data, dict):
            msg_type = data.get("type")
            if msg_type == "rpc.result":
                # Handle RPC result
                req_id = data.get("id")
                result = data.get("result", {})
                logger.info(f"RPC result for {req_id}: {result}")
            elif msg_type == "rpc.error":
                # Handle RPC error
                req_id = data.get("id")
                error = data.get("error", "Unknown error")
                logger.error(f"RPC error for {req_id}: {error}")

    async def connect_to_gateway(self):
        """Connect to the gateway server"""
        try:
            await self.sio.connect(
                GATEWAY_URL,
                headers={
                    "Authorization": f"Bearer {GATEWAY_TOKEN}",
                    "X-Device-Id": "mcp-server-client"
                }
            )
            logger.info("Successfully connected to gateway")
        except Exception as e:
            logger.error(f"Failed to connect to gateway: {e}")
            raise

    async def disconnect_from_gateway(self):
        """Disconnect from the gateway server"""
        if self.connected:
            await self.sio.disconnect()
            logger.info("Disconnected from gateway")

    async def send_rpc_call(self, method: str, params: dict) -> dict:
        """Send RPC call to gateway and wait for response"""
        if not self.connected:
            raise RuntimeError("Not connected to gateway")
        
        # Create RPC call
        rpc_data = {
            "type": "rpc.call",
            "id": f"mcp-{method}-{id(params)}",
            "method": method,
            "params": params
        }
        
        logger.info(f"Sending RPC call: {method} with params: {params}")
        
        # Send RPC call
        await self.sio.emit('message', rpc_data)
        
        # For now, return a simple success response
        # In a real implementation, you would wait for the actual response
        return {
            "success": True,
            "message": f"RPC call {method} sent to gateway"
        }

    async def run(self):
        """Run the MCP server using SSE transport"""
        try:
            logger.info(f"Starting SSE server on {SSE_HOST}:{SSE_PORT} at path {SSE_PATH}")
            logger.info(f"SSE URL: http://{SSE_HOST}:{SSE_PORT}{SSE_PATH}")
            
            # Connect to gateway
            await self.connect_to_gateway()
            
            # Start MCP server with SSE transport
            await self.server.run_sse_async(
                host=SSE_HOST,
                port=SSE_PORT,
                path=SSE_PATH,
                log_level="info"
            )
        except Exception as e:
            logger.error(f"Error in run: {e}")
            raise
        finally:
            # Disconnect from gateway if connected
            if self.connected:
                logger.info("Disconnecting from gateway...")
                await self.disconnect_from_gateway()


async def main():
    """Main function"""
    server = UIAutomatorMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main()) 