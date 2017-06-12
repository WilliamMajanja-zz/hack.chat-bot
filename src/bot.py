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
    """Performs the bots' actions on https://hack.chat.

    The <handle> function is the callback function.
    The <join> function joins channels.
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
        if self._config["github"]:
            self._commands.append("source")
        if self._config["oxfordAppId"] and self._config["oxfordAppKey"]:
            self._commands += ["define", "translate"]
        if self._config["exchangeRateApiKey"]:
            self._commands.append("rate")
        self._oxford = dictionary.Oxford(self._config["oxfordAppId"],
                                         self._config["oxfordAppKey"])

    def handle(self, hackChat, info):
        """Callback function for data sent from https://hack.chat.

        This function is to be used with the "connection" module.
        <hackChat> (callback parameter) is the connection object.
        <info> (callback parameter) is the data sent.
        """
        self._hackChat = hackChat
        if info["type"] == "invite":
            self.join(info["channel"])
        elif info["type"] == "message":
            if info["nick"] != self._config["name"]:
                self._check_afk(info["nick"], info["text"])
            self._post(info["nick"])
            if "trip" in info:
                self._log_trip_code(info["nick"], info["trip"])
            space = re.search(r"\s", info["text"].strip())
            msg = info["text"][space.end():].strip() if space else None
            call = info["text"][:len(self._config["trigger"])]
            if call == self._config["trigger"]:
                check = space.start() if space else len(info["text"])
                cmd = info["text"][len(self._config["trigger"]):check]
                self._message(info["nick"], cmd, msg)
        elif info["type"] == "online add":
            self._post(info["nick"])
        elif info["type"] == "online remove":
            with open("afk.json", "r") as f:
                afkUsers = json.loads(f.read())
            if info["nick"] in afkUsers:
                afkUsers.pop(info["nick"])
                with open("afk.json", "w") as f:
                    json.dump(afkUsers, f, indent = 4)
        elif info["type"] == "stats":
            self._stats(info["IPs"], info["channels"])
        elif info["type"] == "warn":
            self._warn(info["warning"])

    def join(self, channel):
        """Joins the channel <channel> (<str>)."""
        connector = connection.HackChat(
            self.handle, self._config["name"], self._config["password"],
            self._config["url"])
        connector.join(channel)

    def _check_afk(self, nick, msg):
        """Checks for AFK statuses."""
        with open("afk.json", "r") as f:
            afkUsers = json.loads(f.read())
        cmd = "{}afk".format(self._config["trigger"])
        if nick in afkUsers and not re.match(cmd, msg):
            self._hackChat.send("@{} is back: ".format(nick)
                                + "{}".format(afkUsers[nick]))
            afkUsers.pop(nick)
            with open("afk.json", "w") as f:
                json.dump(afkUsers, f, indent = 4)
        reply = ""
        for user in afkUsers:
            person = "@{} ".format(user)
            if person in "{} ".format(msg):
                reply += "{} is AFK: {}\n".format(person, afkUsers[user])
        if reply:
            self._hackChat.send("@{} AFK:\n{}".format(nick, reply))

    def _log_trip_code(self, nick, trip):
        """Logs <nick> and <trip>."""
        with open("trip_codes.json", "r") as f:
            verifiers = json.loads(f.read())
        if trip in verifiers and nick not in verifiers[trip]:
            verifiers[trip].append(nick)
        elif trip not in verifiers:
            verifiers[trip] = [nick]
        with open("trip_codes.json", "w") as f:
            json.dump(verifiers, f, indent = 4)

    def _post(self, nick):
        """Sends messages saved for <nick>."""
        with open("messages.json", "r") as f:
            messages = json.loads(f.read())
        if nick in messages:
            reply = ""
            for msg in messages[nick]:
                reply += ("@{} sent at ".format(msg["sender"])
                          + "{}: {}\n".format(msg["datetime"], msg["message"]))
            messages.pop(nick)
            with open("messages.json", "w") as f:
                json.dump(messages, f, indent = 4)
            self._hackChat.send("@{} you have messages:\n".format(nick)
                                + reply)

    def _stats(self, ipCount, channels):
        """Sends statistics."""
        self._hackChat.send("There are {} unique IPs in ".format(ipCount)
                            + "{} channels.".format(channels))

    def _warn(self, warning):
        """Impure function to handle warnings."""
        print("\nWARNING at {}:\n{}".format(datetime.datetime.now(), warning))

    def _message(self, nick, cmd, msg):
        """Redirects commands to their respective wrapper functions."""
        if cmd == "afk":
            self._afk(nick, msg)
        elif cmd == "define" and "define" in self._commands:
            self._define(nick, msg)
        elif (cmd == "h" and not msg) or cmd == "help":
            self._help_(nick)
        elif cmd == "join":
            self._joiner(nick, msg)
        elif cmd == "joke":
            self._joke(nick)
        elif cmd[:len("katex")] == "katex":
            self._katex_converter(nick, cmd, msg)
        elif cmd[:len("msg")] == "msg":
            self._messenger(nick, cmd, msg)
        elif cmd == "password":
            self._strengthen(nick, msg)
        elif cmd == "poem" or cmd == "poet":
            self._poem(nick, cmd, msg)
        elif cmd[:len("rate")] == "rate" and "rate" in self._commands:
            self._rate(nick, cmd)
        elif cmd == "search":
            self._answer(nick, msg)
        elif cmd == "source" and "source" in self._commands:
            self._source(nick)
        elif cmd == "stats":
            self._get_stats()
        elif cmd == "toss":
            self._toss(nick)
        elif (cmd[:len("translate")] == "translate"
              and "translate" in self._commands):
            self._translate(nick, cmd, msg)
        elif cmd == "urban":
            self._urban(nick, msg)
        elif cmd == "alias":
            self._alias(nick, msg)

    def _afk(self, nick, msg):
        """Handles AFK statuses."""
        with open("afk.json", "r") as f:
            afkUsers = json.loads(f.read())
        afkUsers[nick] = msg
        with open("afk.json", "w") as f:
            json.dump(afkUsers, f, indent = 4)
        self._hackChat.send("@{} is now AFK: {}".format(nick, msg))

    def _answer(self, nick, msg):
        """Handles searches."""
        if msg:
            results = search.duckduckgo(msg, "hack.chat bot")
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
            tell = "@{} ".format(nick)
            reply = utility.shorten(reply, self._maxChars - len(tell), ".")
            if not reply:
                reply = "Sorry, I couldn't find anything."
            self._hackChat.send(tell + reply)
        else:
            self._hackChat.send("@{} instant answers (e.g., ".format(nick)
                                + "{}search ".format(config["trigger"])
                                + "pokemon ruby)")

    def _define(self, nick, msg):
        """Handles definitions."""
        if msg:
            data = self._oxford.define(msg)
            if data["type"] == "success":
                self._hackChat.send("@{} {}: ".format(nick, msg)
                                    + data["response"])
            else:
                self._hackChat.send("@{} Sorry, I couldn't find ".format(nick)
                                    + "any definitions for that.")
        else:
            self._hackChat.send("@{} e.g., ".format(nick)
                                + "{}define hello".format(config["trigger"]))

    def _help_(self, nick):
        """Sends the bots' commands."""
        joinWith = " {}".format(self._config["trigger"])
        reply = joinWith.join(sorted(self._commands))
        self._hackChat.send("@{} {}".format(nick, self._config["trigger"])
                            + reply)

    def _joiner(self, nick, msg):
        """Joins a channel."""
        if msg:
            self._join(msg)
        else:
            self._hackChat.send(
                "@{} joins a hack.chat channel (e.g., ".format(nick)
                + "{}join ben)\nYou can also ".format(config["trigger"])
                + "invite the bot via the sidebar.")

    def _joke(self, nick):
        """Sends jokes."""
        self._hackChat.send("@{} {}".format(nick, jokes.yo_momma()))

    def _katex_converter(self, nick, cmd, msg):
        """Handles KaTeX."""
        colors = ["red", "orange", "green", "blue", "pink", "purple", "gray",
                  "rainbow"]
        sizes = ["tiny", "scriptsize", "footnotesize", "small", "normalsize",
                 "large", "Large", "LARGE", "huge", "Huge"]
        fonts = ["mathrm", "mathit", "mathbf", "mathsf", "mathtt", "mathbb",
                 "mathcal", "mathfrak", "mathscr"]
        if msg:
            disallowed = ("#", "$", "%", "&", "_", "{", "}", "\\", "?")
            if set(msg).isdisjoint(disallowed):
                data = cmd.split(".")
                stringify = lambda value: value if value else ""
                size = stringify(utility.identical_item(data, sizes))
                color = stringify(utility.identical_item(data, colors))
                font = stringify(utility.identical_item(data, fonts))
                txt = katex.generator(msg, size, color, font)
                self._hackChat.send("@{} says {}".format(nick, txt))
            else:
                self._hackChat.send("@{} KaTeX doesn't support \"{}\"".format(
                    nick, "\", \"".join(disallowed)))
        else:
            reply = ("@{} stylizes text (e.g., ".format(nick)
                     + self._config["trigger"]
                     + "katex.rainbow.huge bye)\n")
            optional = lambda x: "\", \"".join(x)
            reply += "OPTIONAL COLORS: \"{}\"\n".format(optional(colors))
            reply += "OPTIONAL SIZES: \"{}\"\n".format(optional(sizes))
            reply += "OPTIONAL FONTS: \"{}\"\n".format(optional(fonts))
            self._hackChat.send(reply)

    def _messenger(self, nick, cmd, msg):
        """Sends saved messages to people when they're next active."""
        info = cmd.split(":")
        if len(info) == 2 and info[1] and msg:
            dt = datetime.datetime.now()
            dt = "{}:{} {}".format(dt.hour, dt.minute, dt.date())
            data = {
                "sender": nick,
                "datetime": dt,
                "message": msg
            }
            with open("messages.json", "r") as f:
                messages = json.loads(f.read())
            if info[1] in messages:
                messages[info[1]].append(data)
            else:
                messages[info[1]] = [data]
            with open("messages.json", "w") as f:
                json.dump(messages, f, indent = 4)
            self._hackChat.send("@{} {} will get your ".format(nick, info[1])
                                + "message the next time they message or "
                                + "join a channel.")
        else:
            self._hackChat.send(
                "@{} sends a message to a user the next time ".format(nick)
                + "they send a message or join a channel (e.g., "
                + "{}msg:ben how are you?)".format(self._config["trigger"]))

    def _poem(self, nick, cmd, msg):
        """Handles poetry."""
        if msg:
            data = poetry.poems(msg, True if cmd == "poet" else False)
            if data:
                data = data[random.randint(0, len(data) - 1)]
                header = "{} by {}".format(data["title"], data["author"])
                if len(header) > 100:
                    header = "{}...".format(header[:97])
                pasted = paste.dpaste(data["poem"], title = header)
                linked = "Read the rest at {}".format(pasted["data"])
                reply = ("@{} {}\nBy: ".format(nick, data["title"])
                         + "{}\n{}".format(data["author"], data["poem"]))
                cut = utility.shorten_lines(reply, self._charsPerLine,
                                            self._maxLines - 1)
                self._hackChat.send(cut + linked)
            else:
                reply = "@{} Sorry, I couldn't find any poems for that."
                self._hackChat.send(reply.format(nick))
        else:
            if cmd == "poem":
                self._hackChat.send(
                    "@{} finds a poem by its name (e.g., ".format(nick)
                    + "{}poem sonnet)".format(self._config["trigger"]))
            else:
                self._hackChat.send(
                    "@{} finds a poem from a poet (e.g., ".format(nick)
                    + "{}poet shakespeare)".format(self._config["trigger"]))

    def _rate(self, nick, cmd):
        """Handles currency conversion."""
        converted = False
        data = cmd.split(":") if ":" in cmd else None
        if data and len(data) == 3:
            fromCode = data[1].upper()
            toCode = data[2].upper()
            if fromCode and toCode:
                data = currency.convert(self._config["exchangeRateApiKey"],
                                        fromCode, toCode)
                if data["type"] == "success":
                    converted = True
                    self._hackChat.send("@{} 1 {} = {} {}".format(
                        nick, fromCode, data["response"], toCode))
        if not converted:
            self._hackChat.send(
                "@{} Sorry, I couldn't convert that. (e.g., ".format(nick)
                + "{}rate:usd:inr gives 1 USD ".format(self._config["trigger"])
                + "= 64 INR)")

    def _source(self, nick):
        """Gives the link to the bots' code."""
        self._hackChat.send("@{} {}".format(nick, self._config["github"]))

    def _strengthen(self, nick, msg):
        """Handles passwords."""
        if msg:
            pwd = password.strengthen(msg)
            self._hackChat.send("@{} {}".format(nick, pwd))
        else:
            self._hackChat.send(
                "@{} strengthens a password (e.g., ".format(nick)
                + "{}password gum)".format(self._config["trigger"]))

    def _get_stats(self):
        """Handles statistics."""
        self._hackChat.stats()

    def _translate(self, nick, cmd, msg):
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
        if msg and len(re.findall(":", cmd)) == 2:
            data = cmd.lower().split(":")
            if data[1] in languages and data[2] in languages:
                explain = False
                srcLang = languages[data[1]]
                targetLang = languages[data[2]]
                words = msg.split()
                translations = []
                for word in words:
                    lastChar = word[len(word) - 1:]
                    symbol = r"[^a-zA-Z]"
                    lastChar = lastChar if re.search(symbol, word) else ""
                    word = re.sub(symbol, "", word)
                    word = oxford.translate(word, targetLang, srcLang)
                    if word["type"] == "failure":
                        translations = []
                        break
                    translations.append(word["response"] + lastChar)
                if translations:
                    translated = " ".join(translations)
                    self._hackChat.send("@{} {}".format(nick, translated))
                else:
                    self._hackChat.send("@{} Sorry, I couldn't ".format(nick)
                                        + "translate it all.")
        if explain:
            self._hackChat.send(
                "@{} supported languages: ".format(nick)
                + "{}\ne.g., ".format(", ".join(languages.keys()))
                + "{}".format(self._config["trigger"])
                + "translate:english:spanish I have a holiday!\n")

    def _toss(self, nick):
        """Handles coin tosses."""
        result = "heads" if random.randint(0, 1) else "tails"
        self._hackChat.send("@{} {}".format(nick, result))

    def _urban(self, nick, msg):
        """Handles urban definitions."""
        if msg:
            data = dictionary.urban(msg)
            if data:
                reply = utility.shorten(data["definition"], self._maxChars,
                                        ".")
                self._hackChat.send(
                    "@{} {}: {} ".format(nick, data["word"], reply)
                    + data["permalink"])
            else:
                self._hackChat.send("@{} Sorry, I couldn't find ".format(nick)
                                    + "any definitions for that.")
        else:
            self._hackChat.send(
                "@{} searches Urban Dictionary (e.g., ".format(nick)
                + "{}urban covfefe)".format(self._config["trigger"]))

    def _alias(self, nick, msg):
        """Verifies trip codes' holdees."""
        if msg:
            with open("trip_codes.json", "r") as f:
                verifiers = json.loads(f.read())
            if msg in verifiers:
                nicks = ", ".join(verifiers[msg])
                self._hackChat.send(
                    "@{} {} has the aliases {}".format(nick, msg, nicks))
            else:
                self._hackChat.send("@{} no aliases were found".format(nick))
        else:
            self._hackChat.send(
                "@{} tells the trip codes' aliases (e.g., ".format(nick)
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
