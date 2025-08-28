#!/usr/bin/env python3
import asyncio
import websockets

async def handler(websocket, path):
    print(f"Connection from {websocket.remote_address}")
    try:
        async for message in websocket:
            print(f"Received: {message}")
            await websocket.send(f"Echo: {message}")
    except websockets.exceptions.ConnectionClosed:
        print("Connection closed")

async def main():
    print("Starting simple WebSocket server on ws://0.0.0.0:8080")
    async with websockets.serve(handler, "0.0.0.0", 8080):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
