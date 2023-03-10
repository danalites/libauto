#!/usr/bin/env python
import asyncio
import websockets

connected = list()

async def hello(websocket):
    connected.append(websocket)
    print("connected: ", connected)
    
    name = await websocket.recv()
    print(f"<<< {name}")
    greeting = f"Hello {name}!"
    await websocket.send(greeting)
    print(f">>> {greeting}")

async def main():
    async with websockets.serve(hello, "localhost", 8765):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())