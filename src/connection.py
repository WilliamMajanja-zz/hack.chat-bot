#!/usr/bin/env python3

import json
import re
import time
import threading
import websocket


class HackChat:
    """This class receives and sends data from and to https://hack.chat.

    Keyword arguments:
    callback -- function; the name of the function to receive data from https://hack.chat
    channel -- string; the channel on https://hack.chat to connect to
    nick -- string; the nickname to use upon connecting
    pwd -- string; the password that generates you a tripcode upon entering

    Usage:
    Access the <onlineUsers> property to get a list of the users currently online in the channel.
    Data received by the callback function will have one of the following formats. More formats exist but those are
    exclusive to the functions in this class accessed by you. All data returned will be of type string.
    {
        "type": "message",
        "nick": <senders' nickname>,
        "text": <senders' message>,
        "trip": <the senders' tripcode if the sender has one>
    }
    {
        "type": "online add",
        "nick": <nickname of user who just joint the channel>
    }
    {
        "type": "online remove",
        "nick": <nickname of user who just left the channel>
    }
    {
        "type": "invite",
        "nick": <nickname of user who invited you to a channel (might be your own if you invited someone else)>,
        "channel": <name of the channel invited to>
    }
    {
        "type": "banned",
        "nick": <nickname of banned user>
    }
    {
        "type": "unbanned",
        "ip": <ip of unbanned user
    }
    {
        "type": "broadcast",
        "text": <the message broadcasted to https://hack.chat>
    }
    {
        "type": "warn",
        "warning": <explanation of why you have been warned>
    }
    The following warnings may be given (more warnings exist for the explicit usage of some functions in this class):
    "You are joining channels too fast. Wait a moment and try again."
    "Nickname must consist of up to 24 letters, numbers, and underscores"
    "Cannot impersonate the admin"
    "Nickname taken"

    Example:
        import connection


        def on_message(connector, data): # Make a callback function with two parameters.
            print(data) # The second parameter (<data>) is the data received.
            print(connector.onlineUsers)
            if data["type"] == "online add": # Check if someone joined the channel.
                connector.send("Hello {}".format(data["nick"])) # Greet the person joining the channel.


        if __name__ == "__main__":
            connection.HackChat(on_message, "bottest", "myBot")
    """

    def __init__(self, callback, channel, nick, pwd = ""):
        """This function initializes values."""
        self.callback = callback
        self.channel = channel
        self.nick = nick
        self.pwd = pwd
        self.onlineUsers = []
        self._ws = websocket.create_connection("wss://hack.chat/chat-ws")
        self._ws.send(json.dumps({"cmd": "join", "channel": self.channel, "nick": "{}#{}".format(self.nick, self.pwd)}))
        threading.Thread(target = self._ping).start()
        threading.Thread(target = self._run).start()

    def _ping(self):
        """This function periodically pings the server to retain the websocket connection."""
        while True:
            time.sleep(60)
            self._ws.send(json.dumps({"cmd": "ping"}))

    def _run(self):
        """This function sends and receives data from https://hack.chat to the callback function."""
        while True:
            result = json.loads(self._ws.recv())
            if result["cmd"] == "chat":
                data = {"type": "message", "nick": result["nick"], "text": result["text"]}
                if "trip" in result:
                    data["trip"] = result["trip"]
                self.callback(self, data)
            elif result["cmd"] == "onlineSet":
                self.onlineUsers += result["nicks"]
            elif result["cmd"] == "onlineAdd":
                self.onlineUsers.append(result["nick"])
                self.callback(self, {"type": "online add", "nick": result["nick"]})
            elif result["cmd"] == "onlineRemove":
                self.onlineUsers.remove(result["nick"])
                self.callback(self, {"type": "online remove", "nick": result["nick"]})
            elif result["cmd"] == "info" and " invited " in result["text"]:
                if "You invited " in result["text"]:
                    name = self.nick
                else:
                    space = re.search(r"\s", result["text"])
                    name = result["text"][:space.start()]
                link = re.search("\?", result["text"])
                channel = result["text"][link.end():]
                self.callback(self, {"type": "invite", "nick": name, "channel": channel})
            elif result["cmd"] == "info" and " IPs " in result["text"]:
                data = result["text"].split()
                self.callback(self, {"type": "stats", "IPs": data[0], "channels": data[4]})
            elif result["cmd"] == "info" and "Banned " in result["text"]:
                self.callback(self, {"type": "banned", "nick": result["text"][len("Banned "):]})
            elif result["cmd"] == "info" and "Unbanned " in result["text"]:
                self.callback(self, {"type": "unbanned", "ip": result["text"][len("Unbanned "):]})
            elif result["cmd"] == "info" and "Server broadcast: " in result["text"]:
                self.callback(self, {"type": "broadcast", "text": result["text"][len("Server broadcast: "):]})
            elif result["cmd"] == "info":
                self.callback(self, {"type": "list users", "text": result["text"]})
            elif result["cmd"] == "warn":
                data = {"type": "warn", "warning": result["text"]}
                if "Could not find " in result["text"]:
                    data["warning"] = "user to ban not found"
                    data["nick"] = result["text"][len("Could not find "):]
                self.callback(self, data)

    def send(self, msg):
        """Use this to send a message <msg> (string) to the channel connected.

        The following data may be sent to the callback function:
        {
            "type": "warn",
            "warning": "You are sending too much text. Wait a moment and try again.\n"
                       + "Press the up arrow key to restore your last message."
        }
        """

        self._ws.send(json.dumps({"cmd": "chat", "text": msg}))

    def invite(self, nick):
        """This sends an invite to the person <nick> (string) to join a randomly generated channel.

        This invite will only be visible to <nick>. The callback function will receive the data such as the channel.
        A warning having one of the following formats might be sent to the callback function.
        {
            "type": "warn",
            "warning": "You are sending invites too fast. Wait a moment before trying again."
        }
        {
            "type": "warn",
            "warning": "Could not find user in channel"
        }
        """

        self._ws.send(json.dumps({"cmd": "invite", "nick": nick}))

    def stats(self):
        """This sends the number of unique IPs and channels on https://hack.chat to the callback function.

        Data of the following format will be sent to the callback function as a result of requesting stats.
        {
            "type": "stats",
            "IPs": <number of unique IPs connected to https://hack.chat>,
            "channels": <number of channels in use on https://hack.chat>
        }
        """

        self._ws.send(json.dumps({"cmd": "stats"}))

    def ban(self, nick):
        """Bans the user <nick> (string) from https://hack.chat for 24 hours.

        <pwd> must be that of a moderators' or admins'. You cannot ban a moderator or admin.
        The callback function will receive data as a result having one of the following formats:
        {
            "type": "warn",
            "warning": "user to ban not found",
            "nick": <the nickname of the user who was to be banned but couldn't be found>
        }
        {
            "type": "warn",
            "warning": "Cannot ban moderator"
        }
        """

        self._ws.send(json.dumps({"cmd": "ban", "nick": nick}))

    def unban(self, ip):
        """Unbans the user having the IP <ip> (string) (<pwd> must be that of a moderators' or admins').

        The callback function will receive data as a result if <nick> was unbanned having the following format.
        {
            "type": "unbanned"
            "ip": <ip of unbanned user>
        }
        """

        self._ws.send(json.dumps({"cmd": "unban", "nick": nick}))

    def list_users(self):
        """This lists the users (<pwd> must be that of an admins').

        This sends data of the form {"type": "list users", "text": <online users>} to the callback function.
        """

        self._ws.send(json.dumps({"cmd": "listUsers"}))

    def broadcast(self, text):
        """Sends <text> (string) to https://hack.chat with this function (<pwd> must be that of an admins').

        The following data will be sent to the callback function.
        {
            "type": "broadcast",
            "text": <the message broadcasted>
        }
        """

        self._ws.send(json.dumps({"cmd": "broadcast", "text": text}))
