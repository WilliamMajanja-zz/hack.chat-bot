#!/usr/bin/env python3

"""Contains impure functions and freeform code to connect the bot."""

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
    """Central callback function."""
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
    """Handles warnings sent from the callback function."""
    data = "\nWARNING at {}:\n{}"
    print(data.format(datetime.datetime.now(), warning))


def join(channel):
    """Join channels."""
    connector = connection.HackChat(callback, config["name"],
                                    config["password"], config["url"])
    connector.join(channel)


def stats(hackChat, ipCount, channels):
    """Sends statistics sent from the callback function."""
    data = "There are {} unique IPs in {} channels."
    hackChat.send(data.format(ipCount, channels))


def message(hackChat, nick, cmd, msg):
    """Handles commands sent from the callback function."""
    if cmd == "define" and "define" in commands:
        define(hackChat, nick, cmd, msg)
    elif (cmd == "h" and not msg) or cmd == "help":
        helper(hackChat, nick, cmd, msg)
    elif cmd == "join":
        joiner(hackChat, nick, cmd, msg)
    elif cmd == "joke":
        joke(hackChat, nick, cmd, msg)
    elif cmd[:len("katex")] == "katex":
        katex_converter(hackChat, nick, cmd, msg)
    elif cmd == "password":
        strengthen(hackChat, nick, cmd, msg)
    elif cmd == "poem" or cmd == "poet":
        poem(hackChat, nick, cmd, msg)
    elif cmd[:len("rate")] == "rate" and "rate" in commands:
        rate(hackChat, nick, cmd, msg)
    elif cmd == "search":
        answer(hackChat, nick, cmd, msg)
    elif cmd == "source" and "source" in commands:
        source(hackChat, nick, cmd, msg)
    elif cmd == "stats":
        get_stats(hackChat, nick, cmd, msg)
    elif cmd == "toss":
        toss(hackChat, nick, cmd, msg)
    elif cmd[:len("translate")] == "translate" and "translate" in commands:
        translate(hackChat, nick, cmd, msg)
    elif cmd == "urban":
        urban(hackChat, nick, cmd, msg)


def define(hackChat, nick, cmd, msg):
    """Handles definitions sent from the callback function."""
    if msg:
        data = oxford.define(msg)
        if data["type"] == "success":
            hackChat.send("@{} {}: {}".format(nick, msg, data["response"]))
        else:
            hackChat.send("@{} Sorry, I couldn't find any ".format(nick)
                          + "definitions for that.")
    else:
        hackChat.send("@{} (e.g., {}define hello)".format(nick,
                                                          config["trigger"]))


def helper(hackChat, nick, cmd, msg):
    """Gives help sent from the callback function."""
    joiner = " {}".format(config["trigger"])
    reply = joiner.join(sorted(commands))
    hackChat.send("@{} {}{}".format(nick, config["trigger"], reply))


def joiner(hackChat, nick, cmd, msg):
    """Joins a channel sent from the callback function."""
    if msg:
        join(msg)
    else:
        hackChat.send("@{} joins a hack.chat channel (e.g., ".format(nick)
                      + "{}join ben)\nYou can also ".format(config["trigger"])
                      + "invite the bot via the sidebar.")


def joke(hackChat, nick, cmd, msg):
    """Handles jokes sent from the callback function."""
    hackChat.send("@{} {}".format(nick, jokes.yo_momma()))


def katex_converter(hackChat, nick, cmd, msg):
    """Handles KaTeX sent from the callback function."""
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


def strengthen(hackChat, nick, cmd, msg):
    """Handles passwords sent from the callback function."""
    if msg:
        pwd = password.strengthen(msg)
        hackChat.send("@{} {}".format(nick, pwd))
    else:
        hackChat.send("@{} strengthens a password (e.g., ".format(nick)
                      + "{}password gum)".format(config["trigger"]))


def poem(hackChat, nick, cmd, msg):
    """Handles poetry sent from the callback function."""
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
            hackChat.send("@{} finds a poem by its name (e.g., ".format(nick)
                          + "{}poem sonnet)".format(config["trigger"]))
        else:
            hackChat.send("@{} finds a poem from a poet (e.g., ".format(nick)
                          + "{}poet shakespeare)".format(config["trigger"]))


def rate(hackChat, nick, cmd, msg):
    """Handles currency conversion sent from the callback function."""
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


def answer(hackChat, nick, cmd, msg):
    """Handles searches sent from the callback function."""
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
        reply = utility.shorten(reply, maxChars - len(tell), ".")
        if not reply:
            reply = "Sorry, I couldn't find anything."
        hackChat.send(tell + reply)
    else:
        hackChat.send("@{} instant answers (e.g., ".format(nick)
                      + "{}search pokemon ruby)".format(config["trigger"]))


def translate(hackChat, nick, cmd, msg):
    """Handles translations sent from the callback function."""
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
                hackChat.send("@{} Sorry, I couldn't translate ".format(nick)
                              + "all of that.")
    if explain:
        hackChat.send("@{} supported languages: ".format(nick)
                      + "{}\ne.g., ".format(", ".join(languages.keys()))
                      + "{}".format(config["trigger"])
                      + "translate:english:spanish I have a holiday!\n")


def source(hackChat, nick, cmd, msg):
    """Handles the bots' source sent from the callback function."""
    hackChat.send("@{} {}".format(nick, config["github"]))


def get_stats(hackChat, nick, cmd, msg):
    """Handles statistics sent from the callback function."""
    hackChat.stats()


def toss(hackChat, nick, cmd, msg):
    """Handles tosses sent from the callback function."""
    result = "heads" if random.randint(0, 1) == 1 else "tails"
    hackChat.send("@{} {}".format(nick, result))


def urban(hackChat, nick, cmd, msg):
    """Handles urban definitions sent from the callback function."""
    if msg:
        data = dictionary.urban(msg)
        if data:
            reply = utility.shorten(data["definition"], maxChars, ".")
            hackChat.send("@{} {}: {} {}".format(nick, data["word"], reply,
                                                 data["permalink"]))
        else:
            hackChat.send("@{} Sorry, I couldn't find any ".format(nick)
                          + "definitions for that.")
    else:
        hackChat.send("@{} searches Urban Dictionary (e.g., ".format(nick)
                      + "{}urban covfefe)".format(config["trigger"]))


random.seed(datetime.datetime.now())
if not os.path.isfile("config.json"):
    data = {}
    print("You can change your configuration later in the file config.json "
          + "located in the src folder. The features whose API tokens you "
          + "don't enter will remain inaccessible until you enter them.")
    data["name"] = input("\nEnter the name of the bot (e.g., myBot) "
                         + "(mandatory): ")
    print("\nA trip code is a randomly generated code based on a password. "
          + "Entering the same password gives the same trip code each time. "
          + "This allows people in anonymous chatting sites to verify if a "
          + "user is who they claim to be regardless of their nickname.")
    data["password"] = getpass.getpass(
        "For privacy, the password will not be shown on the screen while "
        + "you're typing. Enter the password (e.g., myPassword) (optional): ")
    print("\nChannels are chats on https://hack.chat. If the channel for the "
          + "name you enter doesn't exist, one will automatically be created. "
          + "To join the \"math\" channel (https://hack.chat/?math), enter "
          + "\"math\".)")
    data["channel"] = input("Enter which channel you would like to connect to "
                            + "(mandatory): ")
    print("\nFor the bot to know when it's being called, you must state a "
          + "trigger.")
    data["trigger"] = input("Enter the trigger (e.g., \".\" will trigger the "
                            + "bot for \".help\") (mandatory): ")
    url = input("\nEnter the websocket URL of the hack.chat instance to "
                + "connect to (not stating one will enter the original sites' "
                + "websocket URL) (optional): ")
    data["url"] = url if url else "wss://hack.chat/chat-ws"
    data["oxfordAppId"] = input("\nEnter the Oxford Dictionaries API app id "
                                + "(optional): ")
    data["oxfordAppKey"] = input("Enter the Oxford Dictionaries API app key "
                                 "(optional): ")
    data["exchangeRateApiKey"] = input("\nEnter the currency converter API "
                                       + "key (optional): ")
    data["github"] = input("\nEnter the link to the GitHub repository this is "
                           + "on (optional): ")
    print()
    with open("config.json", "w") as f:
        json.dump(data, f, indent = 4)
with open("config.json", "r") as f:
    config = json.loads(f.read())
if not config["name"] or not config["channel"] or not config["trigger"]:
    sys.exit("Make sure you have entered \"name\", \"channel\" and "
             + "\"trigger\" in config.json located in the src folder.")
charsPerLine = 88
maxLines = 8
maxChars = charsPerLine * maxLines
commands = ["h", "help", "join", "joke", "katex", "poem", "poet", "password",
            "search", "stats", "toss", "urban"]
if config["github"]:
    commands.append("source")
if config["oxfordAppId"] and config["oxfordAppKey"]:
    commands += ["define", "translate"]
if config["exchangeRateApiKey"]:
    commands.append("rate")
oxford = dictionary.Oxford(config["oxfordAppId"], config["oxfordAppKey"])
join(config["channel"])
print("\nThe bot has started.")
