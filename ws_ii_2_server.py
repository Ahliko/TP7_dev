import asyncio
import datetime
import json
import os
import uuid
from random import randint
import redis.asyncio as redis
import websockets
from dotenv import load_dotenv


class Server:
    def __init__(self, host, port):
        self.__host = host
        self.__port = port
        self.__websockets = {}
        self.__websockets: dict[str, websockets.WebSocketServerProtocol]
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

    @staticmethod
    async def __get_user(id_: str) -> dict | None:
        client = redis.Redis(host="10.1.1.11", port=6379)
        res = json.loads(await client.get(id_))
        await client.aclose()
        return res

    @staticmethod
    async def __set_user(id_: str, data: dict) -> None:
        client = redis.Redis(host="10.1.1.11", port=6379)
        await client.set(id_, json.dumps(data))
        await client.aclose()

    @staticmethod
    async def get_all_users():
        client = redis.Redis(host="10.1.1.11", port=6379)
        keys = await client.keys()
        await client.aclose()
        return keys

    async def __handle_client_msg(self, websocket: websockets.WebSocketServerProtocol):
        print(f"New client : {websocket.remote_address}")
        if websocket.remote_address not in [(await self.__get_user(i))["addr"] for i in await self.get_all_users()]:
            data = await self.receive(websocket)
            if data == b'':
                await websocket.send("You must choose un nametag")
                await websocket.close()
                return
            elif data.startswith("Hello|"):
                id_ = str(self.generate_uuid())
                self.__websockets[id_] = websocket
                cls = {"here": True, "color": randint(0, 255), 'pseudo': data[6:],
                       "addr": websocket.remote_address}
                await self.__set_user(id_, cls)
                await self.__send(id_, websocket)
                await self.__send_all("", id_, True)
            elif data.split('ID|')[1].encode() in await self.get_all_users():
                id_ = data.split('ID|')[1]
                cls = await self.__get_user(id_)
                cls["here"] = True
                self.__websockets[id_] = websocket
                cls["addr"] = websocket.remote_address
                cls[
                    "timestamp"] = f"[{datetime.datetime.today().hour}:{datetime.datetime.today().minute}]"
                await self.__set_user(id_, cls)
                await self.__send(id_, websocket, accept=True)
                await self.__send_all("", id_, reconnect=True)
            else:
                await websocket.send("You must choose un nametag")
                await websocket.close()
                return
        else:
            id_ = await self.receive(websocket)
            if await self.__get_user(id_) is not None:
                cls = await self.__get_user(id_)
                self.__websockets[id_] = websocket
                cls["here"] = True
                cls["addr"] = websocket.remote_address
                await self.__set_user(id_, cls)
                await self.__send(await self.__get_user(id_), websocket, accept=True)
            else:
                await websocket.send("Connection rejected")
                await websocket.close()
                return
        while True:
            client = await self.__get_user(id_)
            data = await self.receive(websocket)
            if data == b'':
                client["here"] = False
                await websocket.close()
                websocket = None
                print(f"Client {client['pseudo']} disconnected")
                await self.__send_all("", id_, disconnect=True)
                break
            message = data
            client[
                "timestamp"] = f"[{datetime.datetime.today().hour}:{datetime.datetime.today().minute}]"
            print(
                f"Message received from {client['addr'][0]}:{client['addr'][1]} : {message!r}")
            await self.__send_all(message, id_)

    async def __send(self, id_, websocket, accept=False):
        cls = await self.__get_user(id_)
        if accept:
            await websocket.send("200")
        else:
            await websocket.send(f"ID|{id_}")
        await websocket.drain()

    async def __send_all(self, message, localclientid, annonce=False, disconnect=False, reconnect=False):
        localclient = await self.__get_user(localclientid)
        for i in await self.get_all_users():
            client = await self.__get_user(i)
            if client["here"] and i in self.__websockets:
                if not annonce:
                    if client != localclient:
                        if disconnect:
                            print(
                                f"[{datetime.datetime.today().hour}:{datetime.datetime.today().minute}]\033Annonce : {localclient['pseudo']} a quitté la chatroom")
                            await self.__websockets[i].send(
                                f"[{datetime.datetime.today().hour}:{datetime.datetime.today().minute}]\033Annonce : {localclient['pseudo']} a quitté la chatroom")
                            await self.__websockets[i].drain()
                        elif reconnect:
                            print(
                                f"[{datetime.datetime.today().hour}:{datetime.datetime.today().minute}]\033Annonce : {localclient['pseudo']} est de retour !")
                            await self.__websockets[i].send(
                                f"[{datetime.datetime.today().hour}:{datetime.datetime.today().minute}]\033Annonce : {localclient['pseudo']} est de retour !")
                            await self.__websockets[i].drain()
                        else:
                            await self.__websockets[i].send(
                                f"{localclient['timestamp']}\033{localclient['color']}\033{localclient['pseudo']}\033 a dit : {message}")
                            await self.__websockets[i].drain()
                    else:
                        if not disconnect and not reconnect:
                            await self.__websockets[i].send(
                                f"{localclient['timestamp']}\033Vous avez dit : {message}")
                            await self.__websockets[i].drain()
                        elif reconnect:
                            await self.__websockets[i].send(
                                f"{localclient['timestamp']}\033Welcome back  !")
                            await self.__websockets[i].drain()
                else:
                    print(
                        f"[{datetime.datetime.today().hour}:{datetime.datetime.today().minute}]\033Annonce : {localclient['pseudo']} a rejoint la chatroom")

                    await self.__websockets[i].send(
                        f"[{datetime.datetime.today().hour}:{datetime.datetime.today().minute}]\033Annonce : {localclient['pseudo']} a rejoint la chatroom")
                    print(client)
                    await self.__websockets[i].drain()

    async def run(self):
        async with websockets.serve(self.__handle_client_msg, "127.0.0.1", 8888):
            await asyncio.Future()


if __name__ == "__main__":
    load_dotenv(dotenv_path="config")
    Server(os.getenv("HOST"), int(os.getenv("PORT")))
