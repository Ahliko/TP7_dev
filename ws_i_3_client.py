import asyncio
import os.path
import aioconsole
import argparse
import aiofiles
import colored
import json
import websockets


class Client:
    def __init__(self, host="127.0.0.1", port=8888):
        self.__websocket = None
        self.__websocket: websockets.WebSocketClientProtocol
        self.__host = host
        self.__port = port
        self.__uri = f"ws://{self.__host}:{self.__port}"
        self.__pseudo = None
        self.__link = f"{os.path.abspath(os.path.curdir)}/info.json"
        self.__data = {}
        asyncio.run(self.run())

    @staticmethod
    def unjson(data):
        return json.loads(data)

    @staticmethod
    def to_json(data):
        return json.dumps(data)

    @staticmethod
    async def write_content(content, file):
        async with aiofiles.open(file, mode="w") as f:
            await f.write(content)
            await f.flush()

    @staticmethod
    async def read_content(file):
        async with aiofiles.open(file, mode="r") as f:
            return await f.read()

    @staticmethod
    async def decode(reader) -> str | bytes:
        try:
            return await reader.recv()
        except websockets.exceptions.ConnectionClosedOK:
            return b''
        except websockets.exceptions.ConnectionClosedError:
            return b''

    async def __async_input(self):
        while True:
            try:
                input_coro = await aioconsole.ainput("Enter your message: ")
                await self.__websocket.send(input_coro)
                await self.__websocket.drain()
            except KeyboardInterrupt:
                print("Bye!")

                await self.__websocket.close()
                await self.__websocket.wait_closed()
                exit(0)

    async def __async_receive(self):
        while True:
            try:
                data: str | bytes = await self.decode(self.__websocket)
                if data == b'' or data is None:
                    print("Server disconnected")
                    await self.__websocket.close()
                    exit(0)
                message = data
                if message.startswith("Annonce : "):
                    print(colored.stylize(message, colored.fg("red")))
                elif len(message.split("\x1b")) == 4:
                    print("\n" + message.split("\x1b")[0],
                          colored.stylize(message.split("\x1b")[2], colored.fg(message.split("\x1b")[1])) +
                          colored.stylize(message.split("\x1b")[3], colored.fg(15)))
                elif len(message.split("\x1b")) == 2:
                    print("\n" + message.split("\x1b")[0], colored.stylize(message.split("\x1b")[1], colored.fg(15)))
            except KeyboardInterrupt:
                print("Bye!")

                await self.__websocket.close()
                await self.__websocket.wait_closed()
                exit(0)

    async def __async_pseudo(self):
        input_coro = await aioconsole.ainput("Enter your pseudo: ")
        if input_coro == "":
            print("Pseudo cannot be empty.")
            return False
        self.__pseudo = input_coro
        await self.__websocket.send(f"Hello|{self.__pseudo}")
        await self.__websocket.drain()
        data = await self.decode(self.__websocket)
        self.__data["id"] = data.split("|")[1]
        self.to_json(self.__data)
        await self.write_content(self.to_json(self.__data), self.__link)
        return True

    async def __async_id(self):
        await self.__websocket.send(f"ID|{self.__data['id']}")
        await self.__websocket.drain()
        data = await self.decode(self.__websocket)
        if data != "200":
            return False
        return True

    async def run(self):
        try:
            if os.path.exists(self.__link):
                self.__data = await self.read_content(self.__link)
                self.__data = self.unjson(self.__data)
                self.__websocket = await websockets.connect(self.__uri, timeout=10, ping_interval=None)
                if await self.__async_id():
                    while True:
                        await asyncio.gather(*[self.__async_input(),
                                               self.__async_receive()])
                else:
                    print("Connection rejected")
                    os.remove(self.__link)

                    await self.__websocket.close()
                    await self.__websocket.wait_closed()
                    exit(1)
            else:
                self.__websocket = await websockets.connect(self.__uri, timeout=10, ping_interval=None)
                if await self.__async_pseudo():
                    while True:
                        await asyncio.gather(*[self.__async_input(),
                                               self.__async_receive()])
                else:
                    print("Connection rejected")
                    await self.__websocket.close()
                    await self.__websocket.wait_closed()
                    exit(1)
        except KeyboardInterrupt:
            print("Bye!")
            await self.__websocket.close()
            await self.__websocket.wait_closed()
            exit(0)


if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description="Client de chat.")
    argparser.add_argument("-p", "--port", type=int, help="Port de connexion du serveur")
    argparser.add_argument("-a", "--address", type=str, help="Adresse de connexion du serveur")
    argv = argparser.parse_args()
    if argv.port:
        if argv.address:
            Client(host=argv.address, port=argv.port)
        else:
            Client(port=argv.port)
    elif argv.address:
        Client(host=argv.address)
    else:
        Client()
