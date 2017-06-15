#!/usr/bin/env python3

"""Connects the bot."""

import datetime
import getpass
import json
import os.path
import random
import re
import sys
import threading

import connection
import utility
from commands import currency
from commands import jokes
from commands import dictionary
from commands import katex
from commands import password
from commands import paste
from commands import poetry
from commands import search


class HackChatBot:
    """Activates the bot.

    Functions:
    handle: callback
    join: joins channels
    """

    def __init__(self):
        """Initializes values."""
        random.seed(datetime.datetime.now())
        with open("config.json", "r") as f:
            self._config = json.loads(f.read())
        if (not self._config["name"] or not self._config["channel"]
            or not self._config["trigger"]):
            sys.exit("Make sure you have entered \"name\", \"channel\" and "
                     + "\"trigger\" in config.json located in the src folder.")
        self._charsPerLine = 88
        self._maxLines = 8
        self._maxChars = self._charsPerLine * self._maxLines
        self._commands = ["afk", "h", "help", "join", "joke", "katex", "msg",
                          "poem", "poet", "password", "search", "stats",
                          "toss", "urban", "alias"]
        if self._config["oxfordAppId"] and self._config["oxfordAppKey"]:
            self._commands += ["define", "translate"]
        if self._config["exchangeRateApiKey"]:
            self._commands.append("rate")
        self._oxford = dictionary.Oxford(self._config["oxfordAppId"],
                                         self._config["oxfordAppKey"])

    def handle(self, hackChat, info):
        """Callback function for data sent from https://hack.chat.

        <hackChat> (callback parameter) is the connection object.
        <info> (callback parameter) is the data sent.
        """
        self._hackChat = hackChat
        self._type = info["type"]
        self._nick = info["nick"] if "nick" in info else None
        self._text = info["text"].strip() if "text" in info else None
        self._trip = info["trip"] if "trip" in info else None
        self._channel = info["channel"] if "channel" in info else None
        self._ip = info["ip"] if "ip" in info else None
        self._warning = info["warning"] if "warning" in info else None
        self._ips = info["IPs"] if "IPs" in info else None
        self._channels = info["channels"] if "channels" in info else None
        if self._type == "invite":
            self.join(self._channel)
        elif self._type == "message":
            if self._nick != self._config["name"]:
                self._check_afk()
            self._post()
            if self._trip:
                self._log_trip_code()
            space = re.search(r"\s", self._text.strip())
            self._msg = self._text[space.end():].strip() if space else None
            call = self._text[:len(self._config["trigger"])]
            if call == self._config["trigger"]:
                check = space.start() if space else len(self._text)
                self._cmd = self._text[len(self._config["trigger"]):check]
                self._message()
        elif self._type == "online add":
            self._post()
        elif self._type == "online remove":
            with open("afk.json", "r") as f:
                afkUsers = json.loads(f.read())
            if self._nick in afkUsers:
                afkUsers.pop(self._nick)
                with open("afk.json", "w") as f:
                    json.dump(afkUsers, f, indent = 4)
        elif self._type == "stats":
            self._stats()
        elif self._type == "warn":
            self._warn()

    def join(self, channel):
        """Joins the channel <channel> (<str>)."""
        connector = connection.HackChat(
            self.handle, self._config["name"], self._config["password"],
            self._config["url"])
        connector.join(channel)

    def _check_afk(self):
        """Notifies AFK statuses."""
        with open("afk.json", "r") as f:
            afkUsers = json.loads(f.read())
        cmd = "{}afk".format(self._config["trigger"])
        if self._nick in afkUsers and not re.match(cmd, self._text):
            reply = "@{} is back".format(self._nick)
            if afkUsers[self._nick]:
                reply += ": {}".format(afkUsers[self._nick])
            self._hackChat.send(reply)
            afkUsers.pop(self._nick)
            with open("afk.json", "w") as f:
                json.dump(afkUsers, f, indent = 4)
        reply = ""
        for user in afkUsers:
            person = " @{} ".format(user)
            if person in " {} ".format(self._text):
                reply += "{} is AFK".format(person.strip())
                if afkUsers[user]:
                    reply += ": {}".format(afkUsers[user])
                reply += "\n"
        if reply:
            self._hackChat.send("@{} AFK:\n{}".format(self._nick, reply))

    def _log_trip_code(self):
        """Logs nicknames along with their trip codes."""
        with open("trip_codes.json", "r") as f:
            verifiers = json.loads(f.read())
        if self._trip in verifiers and self._nick not in verifiers[self._trip]:
            verifiers[self._trip].append(self._nick)
        elif self._trip not in verifiers:
            verifiers[self._trip] = [self._nick]
        with open("trip_codes.json", "w") as f:
            json.dump(verifiers, f, indent = 4)

    def _post(self):
        """Sends messages saved for people."""
        with open("messages.json", "r") as f:
            messages = json.loads(f.read())
        if self._nick in messages:
            reply = ""
            for msg in messages[self._nick]:
                reply += "@{} sent: {}\n".format(msg["sender"], msg["message"])
            messages.pop(self._nick)
            with open("messages.json", "w") as f:
                json.dump(messages, f, indent = 4)
            self._hackChat.send("@{} you have messages:\n".format(self._nick)
                                + "{}".format(reply))

    def _stats(self):
        """Sends statistics."""
        self._hackChat.send("There are {} unique IPs in ".format(self._ips)
                            + "{} channels.".format(self._channels))

    def _warn(self):
        """Handles warnings."""
        print("\nWARNING at {}:\n{}".format(datetime.datetime.now(),
                                            self._warning))

    def _message(self):
        """Redirects commands to their respective wrapper functions."""
        if self._cmd == "afk":
            self._afk()
        elif self._cmd == "define" and "define" in self._commands:
            self._define()
        elif (self._cmd == "h" and not self._msg) or self._cmd == "help":
            self._help()
        elif self._cmd == "join":
            self._joiner()
        elif self._cmd == "joke":
            self._joke()
        elif self._cmd[:len("katex")] == "katex":
            self._katex_converter()
        elif self._cmd[:len("msg")] == "msg":
            self._messenger()
        elif self._cmd == "password":
            self._strengthen()
        elif self._cmd == "poem" or self._cmd == "poet":
            self._poem()
        elif self._cmd[:len("rate")] == "rate" and "rate" in self._commands:
            self._rate()
        elif self._cmd == "search":
            self._answer()
        elif self._cmd == "stats":
            self._get_stats()
        elif self._cmd == "toss":
            self._toss()
        elif (self._cmd[:len("translate")] == "translate"
              and "translate" in self._commands):
            self._translate()
        elif self._cmd == "urban":
            self._urban()
        elif self._cmd == "alias":
            self._alias()

    def _afk(self):
        """Handles AFK statuses."""
        with open("afk.json", "r") as f:
            afkUsers = json.loads(f.read())
        afkUsers[self._nick] = self._msg
        with open("afk.json", "w") as f:
            json.dump(afkUsers, f, indent = 4)
        reply = "@{} is now AFK".format(self._nick)
        if self._msg:
            reply += ": {}".format(self._msg)
        self._hackChat.send(reply)

    def _answer(self):
        """Handles searches."""
        if self._msg:
            results = search.duckduckgo(self._msg, "hack.chat bot")
            reply = ""
            if len(results["URL"]) > 0:
                reply += "{} ".format(results["URL"])
            if len(results["Heading"]) > 0:
                reply += "{}: ".format(results["Heading"])
            if len(results["Answer"]) > 0:
                reply += results["Answer"]
            elif len(results["AbstractText"]) > 0:
                reply += results["AbstractText"]
            else:
                reply = ""
            tell = "@{} ".format(self._nick)
            reply = utility.shorten(reply, self._maxChars - len(tell), ".")
            if not reply:
                reply = "Sorry, I couldn't find anything."
            self._hackChat.send(tell + reply)
        else:
            self._hackChat.send("@{} instant answers ".format(self._nick)
                                + "(e.g., {}search ".format(config["trigger"])
                                + "pokemon ruby)")

    def _define(self):
        """Handles definitions."""
        if self._msg:
            data = self._oxford.define(self._msg)
            if data["type"] == "success":
                self._hackChat.send("@{} {}: ".format(self._nick, self._msg)
                                    + "{}".format(data["response"]))
            else:
                self._hackChat.send("@{} Sorry, I couldn't ".format(self._nick)
                                    + "find any definitions for that.")
        else:
            self._hackChat.send("@{} e.g., ".format(self._nick)
                                + "{}define hello".format(config["trigger"]))

    def _help(self):
        """Sends a message on how to use the bot."""
        joinWith = " {}".format(self._config["trigger"])
        reply = joinWith.join(sorted(self._commands))
        reply = self._config["trigger"] + reply
        if self._config["github"]:
            reply += "\nsource code: {}".format(self._config["github"])
        self._hackChat.send(
            "@{} {}".format(self._nick, reply))

    def _joiner(self):
        """Joins a channel."""
        if self._msg:
            self.join(self._msg)
        else:
            self._hackChat.send(
                "@{} joins a hack.chat channel (e.g., ".format(self._nick)
                + "{}join ben)\nYou can also ".format(config["trigger"])
                + "invite the bot via the sidebar.")

    def _joke(self):
        """Sends jokes."""
        self._hackChat.send("@{} {}".format(self._nick, jokes.yo_momma()))

    def _katex_converter(self):
        """Handles KaTeX."""
        colors = ["red", "orange", "green", "blue", "pink", "purple", "gray",
                  "rainbow"]
        sizes = ["tiny", "scriptsize", "footnotesize", "small", "normalsize",
                 "large", "Large", "LARGE", "huge", "Huge"]
        fonts = ["mathrm", "mathit", "mathbf", "mathsf", "mathtt", "mathbb",
                 "mathcal", "mathfrak", "mathscr"]
        if self._msg:
            disallowed = ("#", "$", "%", "&", "_", "{", "}", "\\", "?")
            if set(self._msg).isdisjoint(disallowed):
                data = self._cmd.split(".")
                stringify = lambda value: value if value else ""
                size = stringify(utility.identical_item(data, sizes))
                color = stringify(utility.identical_item(data, colors))
                font = stringify(utility.identical_item(data, fonts))
                txt = katex.generator(self._msg, size, color, font)
                self._hackChat.send("@{} says {}".format(self._nick, txt))
            else:
                self._hackChat.send("@{} KaTeX doesn't support \"{}\"".format(
                    self._nick, "\", \"".join(disallowed)))
        else:
            reply = ("@{} stylizes text (e.g., ".format(self._nick)
                     + self._config["trigger"]
                     + "katex.rainbow.huge bye)\n")
            optional = lambda x: "\", \"".join(x)
            reply += "OPTIONAL COLORS: \"{}\"\n".format(optional(colors))
            reply += "OPTIONAL SIZES: \"{}\"\n".format(optional(sizes))
            reply += "OPTIONAL FONTS: \"{}\"\n".format(optional(fonts))
            self._hackChat.send(reply)

    def _messenger(self):
        """Sends saved messages to people when they're next active."""
        info = self._cmd.split(":")
        if len(info) == 2 and info[1] and self._msg:
            data = {
                "sender": self._nick,
                "message": self._msg
            }
            with open("messages.json", "r") as f:
                messages = json.loads(f.read())
            if info[1] in messages:
                messages[info[1]].append(data)
            else:
                messages[info[1]] = [data]
            with open("messages.json", "w") as f:
                json.dump(messages, f, indent = 4)
            self._hackChat.send("@{}, @{} will ".format(self._nick, info[1])
                                + "get your message the next time they message "
                                + "or join a channel.")
        else:
            self._hackChat.send(
                "@{} sends a message to a user the next ".format(self._nick)
                + "time they send a message or join a channel (e.g., "
                + "{}msg:ben how are you?)".format(self._config["trigger"]))

    def _poem(self):
        """Handles poetry."""
        if self._msg:
            isPoet = True if self._cmd == "poet" else False
            data = poetry.poems(self._msg, isPoet)
            if data:
                data = data[random.randint(0, len(data) - 1)]
                header = "{} by {}".format(data["title"], data["author"])
                if len(header) > 100:
                    header = "{}...".format(header[:97])
                pasted = paste.dpaste(data["poem"], title = header)
                linked = "Read the rest at {}".format(pasted["data"])
                reply = ("@{} {}\nBy: ".format(self._nick, data["title"])
                         + "{}\n{}".format(data["author"], data["poem"]))
                cut = utility.shorten_lines(reply, self._charsPerLine,
                                            self._maxLines - 1)
                self._hackChat.send(cut + linked)
            else:
                reply = "@{} Sorry, I couldn't find any poems for that."
                self._hackChat.send(reply.format(self._nick))
        else:
            if self._cmd == "poem":
                self._hackChat.send(
                    "@{} finds a poem by its name (e.g., ".format(self._nick)
                    + "{}poem sonnet)".format(self._config["trigger"]))
            else:
                self._hackChat.send(
                    "@{} finds a poem from a poet (e.g., ".format(self._nick)
                    + "{}poet shakespeare)".format(self._config["trigger"]))

    def _rate(self):
        """Handles currency conversion."""
        converted = False
        data = self._cmd.split(":") if ":" in self._cmd else None
        if data and len(data) == 3:
            fromCode = data[1].upper()
            toCode = data[2].upper()
            if fromCode and toCode:
                data = currency.convert(self._config["exchangeRateApiKey"],
                                        fromCode, toCode)
                if data["type"] == "success":
                    converted = True
                    self._hackChat.send("@{} 1 {} = {} {}".format(
                        self._nick, fromCode, data["response"], toCode))
        if not converted:
            self._hackChat.send(
                "@{} Sorry, I couldn't convert that. ".format(self._nick)
                + "(e.g., {}rate:usd:inr ".format(self._config["trigger"])
                + "gives 1 USD = 64 INR)")

    def _strengthen(self):
        """Handles passwords."""
        if self._msg:
            pwd = password.strengthen(self._msg)
            self._hackChat.send("@{} {}".format(self._nick, pwd))
        else:
            self._hackChat.send(
                "@{} strengthens a password (e.g., ".format(self._nick)
                + "{}password gum)".format(self._config["trigger"]))

    def _get_stats(self):
        """Handles statistics."""
        self._hackChat.stats()

    def _translate(self):
        """Handles translations."""
        languages = {"english": "en",
                     "spanish": "es",
                     "pedi": "nso",
                     "romanian": "ro",
                     "malay": "ms",
                     "zulu": "zu",
                     "indonesian": "id",
                     "tswana": "tn"}
        explain = True
        if self._msg and len(re.findall(":", self._cmd)) == 2:
            data = self._cmd.lower().split(":")
            if data[1] in languages and data[2] in languages:
                explain = False
                srcLang = languages[data[1]]
                targetLang = languages[data[2]]
                words = self._msg.split()
                translations = []
                for word in words:
                    lastChar = word[len(word) - 1:]
                    symbol = r"[^a-zA-Z]"
                    lastChar = lastChar if re.search(symbol, word) else ""
                    word = re.sub(symbol, "", word)
                    word = self._oxford.translate(word, targetLang, srcLang)
                    if word["type"] == "failure":
                        translations = []
                        break
                    translations.append(word["response"] + lastChar)
                if translations:
                    translated = " ".join(translations)
                    self._hackChat.send("@{} {}".format(self._nick,
                                                        translated))
                else:
                    self._hackChat.send("@{} Sorry, I ".format(self._nick)
                                        + "couldn't translate it all.")
        if explain:
            self._hackChat.send(
                "@{} supported languages: ".format(self._nick)
                + "{}\ne.g., ".format(", ".join(languages.keys()))
                + "{}".format(self._config["trigger"])
                + "translate:english:spanish I have a holiday!\n")

    def _toss(self):
        """Handles coin tosses."""
        result = "heads" if random.randint(0, 1) else "tails"
        self._hackChat.send("@{} {}".format(self._nick, result))

    def _urban(self):
        """Handles urban definitions."""
        if self._msg:
            data = dictionary.urban(self._msg)
            if data:
                reply = utility.shorten(data["definition"], self._maxChars,
                                        ".")
                self._hackChat.send(
                    "@{} {}: {} ".format(self._nick, data["word"], reply)
                    + data["permalink"])
            else:
                self._hackChat.send("@{} Sorry, I couldn't ".format(self._nick)
                                    + "find any definitions for that.")
        else:
            self._hackChat.send(
                "@{} searches Urban Dictionary (e.g., ".format(self._nick)
                + "{}urban covfefe)".format(self._config["trigger"]))

    def _alias(self):
        """Sends the requested trip codes' holdees."""
        if self._msg:
            with open("trip_codes.json", "r") as f:
                verifiers = json.loads(f.read())
            if self._msg in verifiers:
                nicks = ", ".join(verifiers[self._msg])
                self._hackChat.send(
                    "@{} {} has the aliases {}".format(self._nick, self._msg,
                                                       nicks))
            else:
                self._hackChat.send(
                    "@{} no aliases were found".format(self._nick))
        else:
            self._hackChat.send(
                "@{} tells the trip codes' aliases (e.g., ".format(self._nick)
                + "{}alias dIhdzE)".format(self._config["trigger"]))


if __name__ == "__main__":
    with open("afk.json", "w") as f:
        json.dump({}, f, indent = 4)
    if not os.path.isfile("messages.json"):
        with open("messages.json", "w") as f:
            json.dump({}, f, indent = 4)
    if not os.path.isfile("trip_codes.json"):
        with open("trip_codes.json", "w") as f:
            json.dump({}, f, indent = 4)
    if not os.path.isfile("config.json"):
        data = {}
        print("You can change your configuration later in the file "
              + "\"config.json\" located in the \"src\" folder. The features "
              + "whose API tokens you don't enter will remain inaccessible "
              + "until you enter them.")
        data["name"] = input("\nEnter the name of the bot (e.g., myBot) "
                             + "(mandatory): ")
        print("\nA trip code is a randomly generated code based on a "
              + "password. Entering the same password gives the same trip "
              + "code each time. This allows people in anonymous chatting "
              + "sites to verify if a user is who they claim to be regardless "
              + "of their nickname.")
        data["password"] = getpass.getpass(
            "For privacy, the password won't be shown on the screen while "
            + "you're typing. Enter the password (e.g., myPassword) "
            + "(optional): ")
        print("\nChannels are chats on https://hack.chat. If the channel for "
              + "the name you enter doesn't exist, one will automatically be "
              + "created. To join the \"math\" channel "
              + "(https://hack.chat/?math), enter \"math\".)")
        data["channel"] = input("Enter which channel you would like to "
                                + "connect to (mandatory): ")
        print("\nFor the bot to know when it's being called, you must state a "
              + "trigger.")
        data["trigger"] = input("Enter the trigger (e.g., \".\" will trigger "
                                + "the bot for \".help\") (mandatory): ")
        url = input("\nEnter the websocket URL of the hack.chat instance to "
                    + "connect to (not stating one will enter the original "
                    + "sites' websocket URL) (optional): ")
        data["url"] = url if url else "wss://hack.chat/chat-ws"
        data["oxfordAppId"] = input("\nEnter the Oxford Dictionaries API app "
                                    + "id (optional): ")
        data["oxfordAppKey"] = input("Enter the Oxford Dictionaries API app "
                                     + "key (optional): ")
        data["exchangeRateApiKey"] = input("\nEnter the currency converter "
                                           + "API key (optional): ")
        data["github"] = input("\nEnter the link to the GitHub repository "
                               + "this is on (optional): ")
        print()
        with open("config.json", "w") as f:
            json.dump(data, f, indent = 4)
    with open("config.json", "r") as f:
        config = json.loads(f.read())
    bot = HackChatBot()
    bot.join(config["channel"])
    print("\nThe bot has started.")
