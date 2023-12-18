# TP7 DEV : Websockets et databases

## Sommaire

- [TP7 DEV : Websockets et databases](#tp7-dev--websockets-et-databases)
  - [Sommaire](#sommaire)
  - [I. Websockets](#i-websockets)
    - [1. First steps](#1-first-steps)
    - [2. Client JS](#2-client-js)
    - [3. Chatroom magueule](#3-chatroom-magueule)
  - [II. Base de données](#ii-base-de-données)
    - [2. Redis](#2-redis)

## I. Websockets

### 1. First steps

🌞 **`ws_i_1_server.py` et `ws_i_1_client.py`**


[ws_i_1_server.py](./ws_i_1_server.py)
[ws_i_1_client.py](./ws_i_1_client.py)
```bash
pip install websockets
pip install aioconsole
sudo firewall-cmd --add-port=8888/tcp --permanent
sudo firewall-cmd --reload

python ws_i_1_server.py
python ws_i_1_client.py
```

### 2. Client JS


🌞 **`ws_i_2_client.js`**

[ws_i_2_client.js](./ws_i_2_client.js)

```bash
npm install ws
node ws_i_2_client.js
```

### 3. Chatroom magueule

🌞 **`ws_i_3_server.py` et `ws_i_3_client.{py,js}`**

[ws_i_3_server.py](./ws_i_3_server.py)
[ws_i_3_client.py](./ws_i_3_client.py)

```bash
pip install websockets
pip install aioconsole
pip install python-dotenv
pip install colored
pip install aiofiles
pip install aioconsole
pip install argparse
sudo firewall-cmd --add-port=8888/tcp --permanent
sudo firewall-cmd --reload

python ws_i_3_server.py
python ws_i_3_client.py -a <ADDR> -p <PORT>
```

## II. Base de données

### 2. Redis

🌞 **`ws_ii_2_server.py`**

[ws_ii_2_server.py](./ws_ii_2_server.py)

```bash
# Installer la base de données redis et modifier le fichier de conf
pip install redis
python ws_ii_2_server.py
```