#!/usr/bin/env python
import json
import asyncio
import websockets

async def hello():
    uri = "ws://localhost:5678"
    async with websockets.connect(uri) as websocket:
        e = {
            "type": "register",
            "value": {
                "worker": "test",
            }
        }

        await websocket.send(json.dumps(e))
        print(f">>> {e}")

        greeting = await websocket.recv()
        print(f"<<< {greeting}")

if __name__ == "__main__":
    asyncio.run(hello())