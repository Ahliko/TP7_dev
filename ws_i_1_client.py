import asyncio

import aioconsole
import websockets


async def run():
    uri = "ws://127.0.0.1:8888"
    try:
        async with websockets.connect(uri, timeout=10, ping_interval=None) as websocket:
            await asyncio.gather(async_send(websocket), async_receive(websocket))
    except websockets.exceptions.ConnectionClosedOK:
        print("Connection closed.")
        exit(0)


async def async_input():
    return await aioconsole.ainput("Enter your message: ")


async def async_send(websocket):
    while True:
        await websocket.send(await async_input())


async def async_receive(websocket):
    while True:
        print(f">>> {await websocket.recv()}")


if __name__ == "__main__":
    asyncio.run(run())
