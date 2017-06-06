#!/usr/bin/env python3

"""Used to connect the bot to https://hack.chat."""

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


def callback(hackChat, info):
    """Impure callback function for the bot."""
    if info["type"] == "invite":
        join(info["channel"])
    elif info["type"] == "message":
        nick = info["nick"]
        space = re.search(r"\s", info["text"].strip())
        msg = info["text"][space.end():] if space else None
        if info["text"][:len(config["trigger"])] == config["trigger"]:
            check = space.start() if space else len(info["text"])
            cmd = info["text"][len(config["trigger"]):check]
            message(hackChat, nick, cmd, msg)
    elif info["type"] == "stats":
        stats(hackChat, info["IPs"], info["channels"])
    elif info["type"] == "warn":
        warn(info["warning"])


def warn(warning):
    """Impure function for warnings sent from the callback function."""
    data = "\nWARNING at {}:\n{}"
    print(data.format(datetime.datetime.now(), warning))


def join(channel):
    """Impure function to join channels on https://hack.chat."""
    connector = connection.HackChat(callback, config["name"],
                                    config["password"], config["url"])
    connector.join(channel)


def stats(hackChat, ipCount, channels):
    """Impure function for statistics sent from the callback function."""
    data = "There are {} unique IPs in {} channels."
    hackChat.send(data.format(ipCount, channels))


def message(hackChat, nick, cmd, msg):
    """Impure function for commands sent from the callback function."""
    if cmd == "define" and "define" in commands:
        if msg:
            data = oxford.define(msg)
            if data["type"] == "success":
                hackChat.send("@{} {}: {}".format(nick, msg, data["response"]))
            else:
                hackChat.send("@{} Sorry, I couldn't find any ".format(nick)
                              + "definitions for that.")
        else:
            hackChat.send("@{} (e.g., {}define hello)".format(
                nick, config["trigger"]))
    elif (cmd == "h" and not msg) or cmd == "help":
        joiner = " {}".format(config["trigger"])
        reply = joiner.join(sorted(commands))
        hackChat.send("@{} {}{}".format(nick, config["trigger"], reply))
    elif cmd == "join":
        if msg:
            join(msg)
        else:
            hackChat.send("@{} joins a hack.chat channel ".format(nick)
                          + "(e.g., {}join ben)\n".format(config["trigger"])
                          + "You can also invite the bot via the sidebar.")
    elif cmd == "joke":
        hackChat.send("@{} {}".format(nick, jokes.yo_momma()))
    elif cmd[:len("katex")] == "katex":
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
                hackChat.send("@{} says {}".format(nick, txt))
            else:
                hackChat.send("@{} KaTeX doesn't support \"{}\"".format(
                    nick, "\", \"".join(disallowed)))
        else:
            reply = ("@{} stylizes text (e.g., ".format(nick)
                     + "{}katex.rainbow.huge bye)\n".format(config["trigger"]))
            optional = lambda x: "\", \"".join(x)
            reply += "OPTIONAL COLORS: \"{}\"\n".format(optional(colors))
            reply += "OPTIONAL SIZES: \"{}\"\n".format(optional(sizes))
            reply += "OPTIONAL FONTS: \"{}\"\n".format(optional(fonts))
            hackChat.send(reply)
    elif cmd == "password":
        if msg:
            pwd = password.strengthen(msg)
            hackChat.send("@{} {}".format(nick, pwd))
        else:
            hackChat.send("@{} strengthens a password ".format(nick)
                          + "(e.g., {}password gum)".format(config["trigger"]))
    elif cmd == "poem" or cmd == "poet":
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
                cut = utility.shorten_lines(reply, charsPerLine, maxLines - 1)
                hackChat.send(cut + linked)
            else:
                reply = "@{} Sorry, I couldn't find any poems for that."
                hackChat.send(reply.format(nick))
        else:
            if cmd == "poem":
                hackChat.send("@{} finds a poem by its name ".format(nick)
                              + "(e.g., {}poem ".format(config["trigger"])
                              + "sonnet)")
            else:
                hackChat.send("@{} finds a poem from a poet ".format(nick)
                              + "(e.g., {}poet ".format(config["trigger"])
                              + "shakespeare)")
    elif cmd[:len("rate")] == "rate" and "rate" in commands:
        converted = False
        data = cmd.split(":") if ":" in cmd else None
        if data and len(data) == 3:
            fromCode = data[1].upper()
            toCode = data[2].upper()
            if fromCode and toCode:
                data = currency.convert(config["exchangeRateApiKey"], fromCode,
                                        toCode)
                if data["type"] == "success":
                    converted = True
                    hackChat.send("@{} 1 {} = {} {}".format(
                        nick, fromCode, data["response"], toCode))
        if not converted:
            hackChat.send("@{} Sorry, I couldn't convert that. ".format(nick)
                          + "(e.g., {}rate:usd:inr ".format(config["trigger"])
                          + "gives 1 USD = 64 INR)")
    elif cmd == "search":
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
            reply = utility.shorten(reply, maxChars, ".")
            finding = reply if reply else "Sorry, I couldn't find anything."
            hackChat.send("@{} {}".format(nick, finding))
        else:
            hackChat.send("@{} instant answers (e.g., ".format(nick)
                          + "{}search pokemon ruby)".format(config["trigger"]))
    elif cmd == "source" and "source" in commands:
        hackChat.send("@{} {}".format(nick, config["github"]))
    elif cmd == "stats":
        hackChat.stats()
    elif cmd == "toss":
        result = "heads" if random.randint(0, 1) == 1 else "tails"
        hackChat.send("@{} {}".format(nick, result))
    elif cmd[:len("translate")] == "translate" and "translate" in commands:
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
                    hackChat.send("@{} {}".format(nick, translated))
                else:
                    hackChat.send("@{} Sorry, I couldn't ".format(nick)
                                  + "translate all of that.")
        if explain:
            hackChat.send("@{} supported languages: ".format(nick)
                          + "{}\n".format(", ".join(languages.keys()))
                          + "e.g., {}".format(config["trigger"])
                          + "translate:english:spanish I have a holiday!\n")
    elif cmd == "urban":
        if msg:
            data = dictionary.urban(msg)
            if data:
                reply = utility.shorten(data["definition"], maxChars, ".")
                hackChat.send("@{} {}: {} {}".format(
                    nick, data["word"], reply, data["permalink"]))
            else:
                hackChat.send("@{} Sorry, I couldn't find any ".format(nick)
                              + "definitions for that.")
        else:
            hackChat.send("@{} searches Urban Dictionary (e.g., ".format(nick)
                          + "{}urban fag)".format(config["trigger"]))


if __name__ == "__main__":
    random.seed(datetime.datetime.now())
    if not os.path.isfile("config.json"):
        print("You can change your configuration later in the file "
              + "config.json located in the src folder. The features whose "
              + "API tokens you don't enter will remain inaccessible until "
              + "you enter them.")
        name = input("\nEnter the name of the bot (e.g., myBot) (mandatory): ")
        print("\nA trip code is a randomly generated code based on a "
              + "password. Entering the same password gives the same trip "
              + "code each time. This allows people in anonymous chatting "
              + "sites to verify if a user is who they claim to be regardless "
              + "of their nickname.")
        pwd = getpass.getpass("For privacy, the password will not be shown on "
                              + "the screen while you're typing. Enter the "
                              + "password (e.g., myPassword) (optional): ")
        print("\nChannels are chats on https://hack.chat. If the channel for "
              + "the name you enter doesn't exist, one will automatically be "
              + "created. To join the \"math\" channel "
              + "(https://hack.chat/?math), enter \"math\".)")
        channel = input("Enter which channel you would like to connect to "
                        + "(mandatory): ")
        print("\nFor the bot to know when it's being called, you must state a "
              + "trigger.")
        trigger = input("Enter the bots trigger (e.g., \".\" will trigger the "
                        "bot for \".help\") (mandatory): ")
        url = input("\nEnter the websocket URL of the hack.chat instance to "
                    + "connect to (not stating one will enter the original "
                    + "sites' websocket URL) (optional): ")
        url = url if url else "wss://hack.chat/chat-ws"
        oxfordAppId = input("\nEnter the Oxford Dictionaries API app id for "
                            + "definitions and translations (optional): ")
        oxfordAppKey = input("Enter the Oxford Dictionaries API app key for "
                             + "definitions and translations (optional): ")
        exchangeRateApiKey = input("\nEnter the currency converter API key "
                                   + "(optional): ")
        github = input("\nEnter the link to the GitHub repository this is on "
                       + "(optional): ")
        print()
        data = {
            "name": name,
            "password": pwd,
            "channel": channel,
            "trigger": trigger,
            "url": url,
            "oxfordAppId": oxfordAppId,
            "oxfordAppKey": oxfordAppKey,
            "exchangeRateApiKey": exchangeRateApiKey,
            "github": github
        }
        with open("config.json", "w") as file_:
            json.dump(data, file_, indent = 4)
    with open("config.json", "r") as f:
        config = json.loads(f.read())
    if not config["name"] or not config["channel"] or not config["trigger"]:
        sys.exit("Make sure you have entered \"name\", \"channel\" and "
                 + "\"trigger\" in config.json located in the src folder.")
    charsPerLine = 88
    maxLines = 8
    maxChars = charsPerLine * maxLines
    commands = ["h", "help", "join", "joke", "katex", "poem", "poet",
                "password", "search", "stats", "toss", "urban"]
    if config["github"]:
        commands.append("source")
    if config["oxfordAppId"] and config["oxfordAppKey"]:
        commands += ["define", "translate"]
    if config["exchangeRateApiKey"]:
        commands.append("rate")
    oxford = dictionary.Oxford(config["oxfordAppId"], config["oxfordAppKey"])
    join(config["channel"])
    print("\nThe bot has started.")
