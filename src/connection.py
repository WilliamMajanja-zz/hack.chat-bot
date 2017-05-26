#!/usr/bin/env python3

import json
import re
import time
import threading
import websocket


class HackChat:
    """This class sends and receives data on a channel on https://hack.chat.

    Keyword arguments:
    channel -- string; the channel on https://hack.chat to connect to
    nick -- string; the nickname to use upon connecting
    pwd -- string; the password that generates you a tripcode upon entering

    Usage:
    Functions:
    send(msg) -- use the <send> function to send a message <msg> (string)
    Properties:
    callbacks -- list of callback functions' names that will receive data
    onlineUsers -- list of users online

    The data received by the callback function(s) will be a dictionary having one of the following forms:
    {"nick": <the nickname of the sender>, "text": <what the sender sent>, "trip": <senders' tripcode if they have one>}
    {"onlineAdd": <the nickname of the user who just joint the channel>}
    {"onlineRemove": <the nickname of the user who just left the channel>}
    {"invite": <the nickname of the person who invited you to a channel>, "channel": <name of channel invited to>}
    {"warn": <an explanation of why you have been warned (e.g., the nickname you used is already taken)>}

    Example:
    import connection # Import the module.
    def on_message(connector, data): # Make a callback function with two parameters.
        print(data) # <data> is the data received.
        print(connector.onlineUsers) # Print a list of the users currently online.
        if "onlineAdd" in data: # Check if someone joined the channel.
            connector.send("Hello {}".format(data["onlineAdd"])) # Greet anyone entering the channel.
    chat = connection.HackChat("bottest", "myBot") # Connect the bot to the channel <bottest> with the name <myBot>.
    chat.callbacks.append(on_message) # Append the name of the callback function to receive data.
    """

    def __init__(self, channel, nick, pwd = ""):
        """Initializes values."""
        self.channel = channel
        self.nick = nick
        self.pwd = pwd
        self.callbacks = []
        self.onlineUsers = []
        self._ws = websocket.create_connection("wss://hack.chat/chat-ws")
        self._ws.send(json.dumps({"cmd": "join", "channel": self.channel, "nick": "{}#{}".format(self.nick, self.pwd)}))
        threading.Thread(target = self._ping).start()
        threading.Thread(target = self._run).start()

    def _ping(self):
        """Periodically pings the server to retain the websocket connection."""
        while True:
            time.sleep(60)
            self._ws.send(json.dumps({"cmd": "ping"}))

    def _run(self):
        """Sends and receives data from https://hack.chat."""
        while True:
            result = json.loads(self._ws.recv())
            if result["cmd"] == "chat":
                data = {"nick": result["nick"], "text": result["text"]}
                if "trip" in result:
                    data["trip"] = result["trip"]
                for callback in self.callbacks:
                    callback(self, data)
            elif result["cmd"] == "onlineSet":
                self.onlineUsers += result["nicks"]
            elif result["cmd"] == "onlineAdd":
                self.onlineUsers.append(result["nick"])
                for callback in self.callbacks:
                    callback(self, {"onlineAdd": result["nick"]})
            elif result["cmd"] == "onlineRemove":
                self.onlineUsers.remove(result["nick"])
                for callback in self.callbacks:
                    callback(self, {"onlineRemove": result["nick"]})
            elif result["cmd"] == "info":
                space = re.search(r"\s", result["text"])
                name = result["text"][:space.start()]
                link = re.search("\?", result["text"])
                channel = result["text"][link.end():]
                for callback in self.callbacks:
                    callback(self, {"invite": name, "channel": channel})
            elif result["cmd"] == "warn":
                for callback in self.callbacks:
                    callback(self, {"warn": result["text"]})

    def send(self, msg):
        """Sends <msg> (string) on the channel connected."""
        self._ws.send(json.dumps({"cmd": "chat", "text": msg}))
