import asyncio
import websockets


async def receive(websocket):
    try:
        while True:
            string = await websocket.recv()
            print(f"<<< {string}")
            greeting = f'Hello client ! Received "{string}"'
            await websocket.send(greeting)
            print(f">>> {greeting}")
    except websockets.exceptions.ConnectionClosedOK:
        print("Connection closed.")


async def main():
    async with websockets.serve(receive, "127.0.0.1", 8888):
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
