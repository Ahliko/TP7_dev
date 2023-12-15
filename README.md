# TP7 DEV : Websockets et databases

## Sommaire

- [TP7 DEV : Websockets et databases](#tp7-dev--websockets-et-databases)
  - [Sommaire](#sommaire)
  - [I. Websockets](#i-websockets)
    - [1. First steps](#1-first-steps)
    - [2. Client JS](#2-client-js)
    - [3. Chatroom magueule](#3-chatroom-magueule)
  - [II. Base de données](#ii-base-de-données)
    - [1. Intro données](#1-intro-données)
    - [2. Redis](#2-redis)
    - [3. Bonus : MongoDB](#3-bonus--mongodb)

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

### 1. Intro données

➜ Bon dans le cadre du chat, **les données** c'est :

- **la variable globale `clients`**
  - contient toutes les infos des clients connectés : les sessions
  - c'est une donnée très "chaude" qui change tout le temps
- **l'historique du chat**
  - *si t'as fait le bonus, sinon, tu fais genre*
  - une donnée plutôt "tiède" (personne ne dit ça) : accédée assez régulièrement mais ça va
  - on accède pas à tout en même temps :
    - soit on ajoute le dernier message à l'historique
    - soit on lit les N derniers messages pour les envoyer à un client qui se co
    - on modifie jamais une donnée existante

➜ L'idée c'est :

- on veut **pas garder les données dans notre application**, c'est trop fragile
  - donc *exit* la variable globale qui stocke tout
- on veut sortir les données pour les stocker à un endroit dédié
- on pourrait stocker ça sur le disque
  - certains ont fait ça pour le chat au TP6 (format JSON)
  - mais ça rame sa mère le disque, surtout quand le fichier va grossir
  - et on fait comment quand il faut deux serveurs pour soutenir la charge ? Un fichier partagé ? Woah le bordel. Et s'ils modifient à deux le même fichier ? Woah le bordel.
  - *exit* le stockage sur disque
- **le remède : stocker ça en base de données**
  - pour une base, les données sont essentiellement en RAM
  - c'est fast
  - on déporte la gestion des données vers une autre application
  - si cette base de données est sur une autre machine que notre application il faut utiliser... le réseau ! LA BOUCLE EST BOUCLÉE.

➜ **On va aussi stocker/interagir avec les données différemment suivant leur "température"**.

Ici on aimerait :

- **un stockage petit mais très performant pour stocker nos "sessions"**
  - équivalent de la variable globale `client`
  - on a même pas besoin de conserver ça entre les redémarrages limite
  - on va utiliser une base de données Redis
- **un stockage + orienté longue durée pour stocker l'historique**
  - on va utiliser une base de données MongoDB

> *Ouais donc, base de données, mais pas de SQL. La vie est belle.*

### 2. Redis

➜ **Pour installer Redis**

- soit vous gérez votre truc (Docker en local ?)
- soit vous popez une VM Rocky Linux et vous exécuter les commandes suivantes :
  - nécessaire d'avoir une connexion internet dans la VM
  - nécessaire de se co en SSH pour copy/paste mes commandes
  - les commandes :

```bash
# on installe docker vitefé
$ sudo yum install -y yum-utils
$ sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
$ sudo yum install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
$ sudo systemctl enable --now docker

# on lance un ptit conteneur qui tournera à l'infini avec redis dedans
$ sudo docker run -d -p 6379:6379 --restart=always redis
```

Une fois que c'est fait, y'a Redis disponible (depuis votre poste ou une autre VM) à l'adresse : `<IP_VM_REDIS>:6379`.

➜ **P'tit coup de pouce pour la syntaxe de la lib Python `redis` :**

```python
import asyncio
import redis.asyncio as redis # on utilise la version asynchrone de la lib

async def main():
    # connexion au serveur Redis
    client = redis.Redis(host="10.1.1.1", port=6379)
    
    # on définit la clé 'cat' à la valeur 'meo'
    await client.set('cat', 'meow')
    # on définit la clé 'dog' à la valeur 'waf'
    await client.set('dog', 'waf')

    # récupération de la valeur de 'cat'
    what_the_cat_says = await client.get('cat')

    # ça devrait print 'meow'
    print(what_the_cat_says)

    # on ferme la connexion proprement
    await client.aclose()

if __name__ == "__main__":
    asyncio.run(main())
```

🌞 **`ws_ii_2_server.py`**

- adaptez-votre code serveur précédent
- celui-ci n'utilise pas du tout de variable globale `client`
- à la place, il utilise une base de données Redis :
  - ajout d'une donnée quand un nouveau client arrive
  - suppression/modification d'une donnée quand un client s'en va
  - tous les appels à la base de données doivent être asynchrones

### 3. Bonus : MongoDB

🌞 **`ws_ii_3_server.py`**

- bonus-ception vu que l'historique était déjà un bonus
- le serveur stocke l'historique des messages dans une base MongoDB
- il faut donc setup un serveur MongoDB et avoir une lib Python adaptée

![t'as la réf ?](./img/talaref.png)