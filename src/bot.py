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
    if info["type"] == "warn":
        data = "\nWARNING at {}:\n{}"
        print(data.format(datetime.datetime.now(), info["warning"]))
    elif info["type"] == "invite":
        connector = connection.HackChat(callback, config["name"],
                                        config["password"], config["url"])
        connector.join(info["channel"])
    elif info["type"] == "stats":
        data = "There are {} unique IPs in {} channels."
        hackChat.send(data.format(info["IPs"], info["channels"]))
    if info["type"] != "message":
        return
    roughMaxLen = 83 * 4
    isCmd = lambda cmd: info["text"][:len(config["trigger"] + cmd)] \
                        == config["trigger"] + cmd
    space = re.search(r"\s", info["text"].strip())
    if isCmd("about") and config["github"]:
        hackChat.send("@{} {}".format(info["nick"], config["github"]))
    elif (isCmd("define") and config["oxfordAppId"]
          and config["oxfordAppKey"]):
        if space:
            data = oxford.define(info["text"][space.end():])
            if data["type"] == "success":
                hackChat.send("@{} {}: {}".format(
                    info["nick"], info["text"][space.end():],
                    data["response"]))
            else:
                hackChat.send("@{} Sorry, I couldn't find".format(info["nick"])
                              + "any definitions for that.")
        else:
            hackChat.send("@{} (e.g., {}define hello)".format(
                info["nick"], config["trigger"]))
    elif ((isCmd("h") and
           len(info["text"].strip()) == len(config["trigger"] + "h"))
          or isCmd("help")):
        commands = ["h", "help", "join", "joke", "katex", "poem",
                    "poet", "password", "search", "stats", "toss", "urban"]
        if config["github"]:
            commands.append("about")
        if config["oxfordAppId"] and config["oxfordAppKey"]:
            commands += ["define", "translate"]
        if config["exchangeRateApiKey"]:
            commands.append("rate")
        reply = " {}".format(config["trigger"]).join(sorted(commands))
        hackChat.send("@{} {}{}".format(info["nick"], config["trigger"],
                                        reply))
    elif isCmd("join"):
        if space:
            connector = connection.HackChat(callback, config["name"],
                                            config["password"], config["url"])
            connector.join(info["text"][space.end():])
        else:
            hackChat.send("@{} joins a hack.chat channel ".format(info["nick"])
                          + "(e.g., {}join ben)\n".format(config["trigger"])
                          + "You can also invite the bot via the sidebar.")
    elif isCmd("joke"):
        hackChat.send("@{} {}".format(info["nick"], jokes.yo_momma()))
    elif isCmd("katex"):
        colors = ["red", "orange", "green", "blue", "pink", "purple", "gray",
                  "rainbow"]
        sizes = ["tiny", "scriptsize", "footnotesize", "small", "normalsize",
                 "large", "Large", "LARGE", "huge", "Huge"]
        fonts = ["mathrm", "mathit", "mathbf", "mathsf", "mathtt", "mathbb",
                 "mathcal", "mathfrak", "mathscr"]
        if space:
            msg = info["text"][space.end():]
            disallowed = ("#", "$", "%", "&", "_", "{", "}", "\\", "?")
            if set(msg).isdisjoint(disallowed):
                data = info["text"][:space.start()].split(".")
                stringify = lambda value: value if value else ""
                size = stringify(utility.identical_item(data, sizes))
                color = stringify(utility.identical_item(data, colors))
                font = stringify(utility.identical_item(data, fonts))
                txt = katex.generator(msg, size, color, font)
                hackChat.send("@{} says {}".format(info["nick"], txt))
            else:
                hackChat.send("@{} KaTeX doesn't support {}".format(
                    info["nick"], disallowed.join(", ")))
        else:
            reply = ("@{} stylizes text (e.g., ".format(info["nick"])
                     + "{}katex.rainbow.huge".format(config["trigger"])
                     + " hello)\n")
            optional = lambda x: "\", \"".join(x)
            reply += "OPTIONAL COLORS: \"{}\"\n".format(optional(colors))
            reply += "OPTIONAL SIZES: \"{}\"\n".format(optional(sizes))
            reply += "OPTIONAL FONTS: \"{}\"\n".format(optional(fonts))
            hackChat.send(reply)
    elif isCmd("password"):
        if space:
            pwd = password.strengthen(info["text"][space.end():])
            hackChat.send("@{} {}".format(info["nick"], pwd))
        else:
            hackChat.send("@{} strengthens a password ".format(info["nick"])
                          + "(e.g., {}password ".format(config["trigger"])
                          + "gum)")
    elif isCmd("poem") or isCmd("poet"):
        if space:
            find = info["text"][space.end():]
            data = poetry.poems(find, True if isCmd("poet") else False)
            if data:
                data = data[random.randint(0, len(data) - 1)]
                poem = utility.shorten(data["poem"], int(roughMaxLen / 2), ",")
                header = "{} by {}".format(data["title"], data["author"])
                if len(header) > 100:
                    header = "{}...".format(header[:97])
                pasted = paste.dpaste(data["poem"], title = header)
                hackChat.send("@{} {}".format(info["nick"], data["title"])
                              + "\nBy: {}\n{}\n".format(data["author"], poem)
                              + "Read the rest at {}".format(pasted["data"]))
            else:
                reply = "@{} Sorry, I couldn't find any poems for that."
                hackChat.send(reply.format(info["nick"]))
        else:
            if isCmd("poem"):
                hackChat.send("@{} finds a poem by its ".format(info["nick"])
                              + "name (e.g., {}".format(config["trigger"])
                              + "poem sonnet)")
            else:
                hackChat.send("@{} finds a poem from a ".format(info["nick"])
                              + "poet (e.g., {}".format(config["trigger"])
                              + "poet shakespeare)")
    elif isCmd("rate") and config["exchangeRateApiKey"]:
        converted = False
        msg = info["text"][:space.start()] if space else info["text"]
        data = msg.split(":")
        if len(data) == 3:
            fromCode = data[1]
            toCode = data[2]
            if fromCode and toCode:
                data = currency.convert(config["exchangeRateApiKey"], fromCode,
                                        toCode)
                if data["type"] == "success":
                    converted = True
                    hackChat.send("@{} 1 {} = {} {}".format(
                        info["nick"], fromCode.upper(), data["response"],
                        toCode.upper()))
        if not converted:
            hackChat.send("@{} Sorry, I couldn't convert ".format(info["nick"])
                          + "that. (e.g., {}".format(config["trigger"])
                          + "rate:usd:inr gives 1 USD = 64 INR)")
    elif isCmd("search"):
        if space:
            results = search.duckduckgo(info["text"][space.end():],
                                        "hack.chat bot")
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
            reply = utility.shorten(reply, roughMaxLen, ".")
            finding = reply if reply else "Sorry, I couldn't find anything."
            hackChat.send("@{} {}".format(info["nick"], finding))
        else:
            hackChat.send("@{} instant answers ".format(info["nick"])
                          + "(e.g., {}search ".format(config["trigger"])
                          + "pokemon ruby)")
    elif isCmd("stats"):
        hackChat.stats()
    elif isCmd("toss"):
        result = "heads" if random.randint(0, 1) == 1 else "tails"
        hackChat.send("@{} {}".format(info["nick"], result))
    elif (isCmd("translate") and config["oxfordAppId"]
          and config["oxfordAppKey"]):
        languages = {"english": "en",
                     "spanish": "es",
                     "pedi": "nso",
                     "romanian": "ro",
                     "malay": "ms",
                     "zulu": "zu",
                     "indonesian": "id",
                     "tswana": "tn"}
        translatable = True
        if space and len(re.findall(":", info["text"][:space.start()])) == 2:
            data = info["text"][:space.start()]
            data = data.lower().split(":")
            if data[1] in languages and data[2] in languages:
                srcLang = languages[data[1]]
                targetLang = languages[data[2]]
                words = info["text"][space.end():].split()
                translations = []
                for word in words:
                    lastChar = word[len(word) - 1:]
                    symbol = r"[^a-zA-Z\s]"
                    lastChar = lastChar if re.search(symbol, word) else ""
                    word = re.sub(symbol, "", word)
                    word = oxford.translate(word, targetLang, srcLang)
                    if word["type"] == "failure":
                        translations = []
                        break
                    translations.append(word["response"] + lastChar)
                if translations:
                    translated = " ".join(translations)
                    hackChat.send("@{} {}".format(info["nick"], translated))
                else:
                    hackChat.send("@{} Sorry, I ".format(info["nick"])
                                  + "couldn't translate all of that.")
            else:
                translatable = False
        else:
            translatable = False
        if not translatable:
            hackChat.send("@{} supported languages: ".format(info["nick"])
                          + "{}\n".format(", ".join(languages.keys()))
                          + "e.g., {}".format(config["trigger"])
                          + "translate:english:spanish I have a holiday!\n"
                          + "will translate from from English to Spanish")
    elif isCmd("urban"):
        if space:
            data = dictionary.urban(info["text"][space.end():])
            if data:
                reply = utility.shorten(data["definition"], roughMaxLen, ".")
                hackChat.send("@{} {}: {} {}".format(
                    info["nick"], data["word"], reply, data["permalink"]))
            else:
                hackChat.send("@{} Sorry, I couldn't ".format(info["nick"])
                              + "find any definitions for that.")
        else:
            hackChat.send("@{} searches Urban Dictionary ".format(info["nick"])
                          + "(e.g., {}urban fag)".format(config["trigger"]))


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
    oxford = dictionary.Oxford(config["oxfordAppId"], config["oxfordAppKey"])
    connector = connection.HackChat(callback, config["name"],
                                    config["password"], config["url"])
    connector.join(config["channel"])
    print("\nThe bot has started.")
