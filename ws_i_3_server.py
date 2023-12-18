import asyncio
import datetime
import os
import uuid
from random import randint
import websockets
from dotenv import load_dotenv


class Server:
    def __init__(self, host, port):
        self.__host = host
        self.__port = port
        self.__clients = {}
        self.__clients["w"]: websockets.WebSocketServerProtocol
        asyncio.run(self.run())

    @staticmethod
    def generate_uuid():
        return uuid.uuid4()

    @staticmethod
    async def receive(reader) -> str | bytes:
        try:
            return await reader.recv()
        except websockets.exceptions.ConnectionClosedOK:
            return b''
        except websockets.exceptions.ConnectionClosedError:
            return b''

    async def __handle_client_msg(self, websocket: websockets.WebSocketServerProtocol):
        print(f"New client : {websocket.remote_address}")
        if websocket.remote_address not in [i["addr"] for i in self.__clients.values()]:
            data = await self.receive(websocket)
            if data == b'':
                await websocket.send("You must choose un nametag")
                await websocket.close()
                return
            elif data.startswith("Hello|"):
                id_ = str(self.generate_uuid())
                self.__clients[id_] = {}
                self.__clients[id_]["w"] = websocket
                self.__clients[id_]["here"] = True
                self.__clients[id_]["color"] = randint(0, 255)
                self.__clients[id_]['pseudo'] = data[6:]
                self.__clients[id_]["addr"] = websocket.remote_address
                await self.__send(id_)
                await self.__send_all("", id_, True)
            elif data.split('ID|')[1] in self.__clients:
                id_ = data.split('ID|')[1]
                self.__clients[id_]["w"] = websocket
                self.__clients[id_]["here"] = True
                self.__clients[id_]["addr"] = websocket.remote_address
                self.__clients[id_][
                    "timestamp"] = f"[{datetime.datetime.today().hour}:{datetime.datetime.today().minute}]"
                await self.__send(id_, accept=True)
                await self.__send_all("", id_, reconnect=True)
            else:
                await websocket.send("You must choose un nametag")
                await websocket.close()
                return
        else:
            id_ = await self.receive(websocket)
            if id_ in self.__clients:
                self.__clients[id_]["w"] = websocket
                self.__clients[id_]["here"] = True
                self.__clients[id_]["addr"] = websocket.remote_address
                await self.__send(id_, accept=True)
            else:
                await websocket.send("Connection rejected")
                await websocket.close()
                return
        while True:
            data = await self.receive(self.__clients[id_][
                                          "w"])
            client = id_
            if data == b'':
                self.__clients[client]["here"] = False
                await self.__clients[client]["w"].close()
                self.__clients[client]["w"] = None
                print(f"Client {self.__clients[client]['pseudo']} disconnected")
                await self.__send_all("", client, disconnect=True)
                break
            message = data
            self.__clients[client][
                "timestamp"] = f"[{datetime.datetime.today().hour}:{datetime.datetime.today().minute}]"
            print(
                f"Message received from {self.__clients[client]['addr'][0]}:{self.__clients[client]['addr'][1]} : {message!r}")
            await self.__send_all(message, client)

    async def __send(self, id_, accept=False):
        if accept:
            await self.__clients[id_]["w"].send("200")
        else:
            await self.__clients[id_]["w"].send(f"ID|{id_}")
        await self.__clients[id_]["w"].drain()

    async def __send_all(self, message, localclient, annonce=False, disconnect=False, reconnect=False):
        for client in self.__clients:
            if self.__clients[client]["here"]:
                if not annonce:
                    if client != localclient:
                        if disconnect:
                            print(
                                f"[{datetime.datetime.today().hour}:{datetime.datetime.today().minute}]\033Annonce : {self.__clients[localclient]['pseudo']} a quitté la chatroom")
                            await self.__clients[client]["w"].send(
                                f"[{datetime.datetime.today().hour}:{datetime.datetime.today().minute}]\033Annonce : {self.__clients[localclient]['pseudo']} a quitté la chatroom")
                            await self.__clients[client]["w"].drain()
                        elif reconnect:
                            print(
                                f"[{datetime.datetime.today().hour}:{datetime.datetime.today().minute}]\033Annonce : {self.__clients[localclient]['pseudo']} est de retour !")
                            await self.__clients[client]["w"].send(
                                f"[{datetime.datetime.today().hour}:{datetime.datetime.today().minute}]\033Annonce : {self.__clients[localclient]['pseudo']} est de retour !")
                            await self.__clients[client]["w"].drain()
                        else:
                            await self.__clients[client]["w"].send(
                                f"{self.__clients[localclient]['timestamp']}\033{self.__clients[localclient]['color']}\033{self.__clients[localclient]['pseudo']}\033 a dit : {message}")
                            await self.__clients[client]["w"].drain()
                    else:
                        if not disconnect and not reconnect:
                            await self.__clients[client]["w"].send(
                                f"{self.__clients[localclient]['timestamp']}\033Vous avez dit : {message}")
                            await self.__clients[client]["w"].drain()
                        elif reconnect:
                            await self.__clients[client]["w"].send(
                                f"{self.__clients[localclient]['timestamp']}\033Welcome back  !")
                            await self.__clients[client]["w"].drain()
                else:
                    print(
                        f"[{datetime.datetime.today().hour}:{datetime.datetime.today().minute}]\033Annonce : {self.__clients[localclient]['pseudo']} a rejoint la chatroom")

                    await self.__clients[client]["w"].send(
                        f"[{datetime.datetime.today().hour}:{datetime.datetime.today().minute}]\033Annonce : {self.__clients[localclient]['pseudo']} a rejoint la chatroom")
                    print(client)
                    await self.__clients[client]["w"].drain()

    async def run(self):
        async with websockets.serve(self.__handle_client_msg, self.__host, self.__port):
            await asyncio.Future()


if __name__ == "__main__":
    load_dotenv(dotenv_path="config")
    Server(os.getenv("HOST"), int(os.getenv("PORT")))
