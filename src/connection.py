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
    stats -- this sends a request for the number of unique IPs connected to channels on https://hack.chat. The result
             of this function will be sent to the callback function(s).
    Properties:
    callbacks -- list of callback functions' names that will receive data
    onlineUsers -- list of users online

    The data received by the callback function(s) will be a dictionary having one of the following formats:
    {
        "type": "message",
        "nick": <senders' nickname>,
        "text": <senders' message>,
        "trip": <senders' tripcode if the sender has one>
    }
    {
        "type": "onlineAdd",
        "nick": <nickname of user who just joint the channel>
    }
    {
        "type": "onlineRemove",
        "nick": <nickname of user who just left the channel>
    }
    {
        "type": "invite",
        "nick": <nickname of user who invited you to a channel>,
        "channel": <name of the channel invited to>
    }
    {
        "type": "stats",
        "IPs": <number of unique IPs connected to https://hack.chat>,
        "channels": <number of channels in use on https://hack.chat>
    }
    {
        "type": "warn",
        "warning": <explanation of why you have been warned (e.g., nickname you used is already taken)>
    }

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
                data = {"type": "message", "nick": result["nick"], "text": result["text"]}
                if "trip" in result:
                    data["trip"] = result["trip"]
                for callback in self.callbacks:
                    callback(self, data)
            elif result["cmd"] == "onlineSet":
                self.onlineUsers += result["nicks"]
            elif result["cmd"] == "onlineAdd":
                self.onlineUsers.append(result["nick"])
                for callback in self.callbacks:
                    callback(self, {"type": "onlineAdd", "nick": result["nick"]})
            elif result["cmd"] == "onlineRemove":
                self.onlineUsers.remove(result["nick"])
                for callback in self.callbacks:
                    callback(self, {"type": "onlineRemove", "nick": result["nick"]})
            elif result["cmd"] == "info" and " invited " in result["text"]:
                space = re.search(r"\s", result["text"])
                name = result["text"][:space.start()]
                link = re.search("\?", result["text"])
                channel = result["text"][link.end():]
                for callback in self.callbacks:
                    callback(self, {"type": "invite", "nick": name, "channel": channel})
            elif result["cmd"] == "info" and " IPs " in result["text"]:
                data = result["text"].split()
                for callback in self.callbacks:
                    callback(self, {"type": "stats", "IPs": data[0], "channels": data[4]})
            elif result["cmd"] == "warn":
                for callback in self.callbacks:
                    callback(self, {"type": "warn", "warning": result["text"]})

    def send(self, msg):
        """Sends <msg> (string) on the channel connected."""
        self._ws.send(json.dumps({"cmd": "chat", "text": msg}))

    def stats(self):
        """Requests the statistics of connections on https://hack.chat."""
        self._ws.send(json.dumps({"cmd": "stats"}))
