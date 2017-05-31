#!/usr/bin/env python3

"""This is used to connect the bot to https://hack.chat using credentials from the file credentials.py."""

import datetime
import getpass
import os.path
import random
import re
import sys
import threading

import connection
from commands import currency, jokes, dictionary, katex, password, paste, poetry, search

if not os.path.isfile("credentials.py"):
    with open("credentials.py", "w") as f:
        print("You can change your credentials later in the file credentials.py located in the src folder. The features"
              + "whose API tokens you don't enter will remain inaccessible until you enter them.")
        name = input("Enter the name of the bot (e.g., myBot) (mandatory): ")
        print("\nA trip code is a randomly generated code based on a password. Entering the same password gives the "
              + "same trip code each time. This allows people in anonymous chatting sites to verify if a user is who "
              + "they claim to be regardless of their nickname.")
        pwd = getpass.getpass("For privacy, the password will not be shown on the screen when you're typing. "
                              + "Enter the password for the trip code (e.g., myPassword) (optional): ")
        print("\nChannels are chats on https://hack.chat. If the channel for the name you enter doesn't exist, one will"
              + "automatically be created. To join the \"math\" channel (https://hack.chat/?math), enter \"math\".)")
        channel = input("Enter which channel you would like to connect to (mandatory): ")
        print("\nFor the bot to know when it's being called, you must state a trigger.")
        trigger = input("Enter the bots trigger (e.g., \".\" will trigger the bot for \".help\") (mandatory): ")
        oxfordAppId = input("\nEnter the Oxford Dictionaries API app id for definitions and translations (optional): ")
        oxfordAppKey = input("Enter the Oxford Dictionaries API app key for definitions and translations (optional): ")
        exchangeRateApiKey = input("\nEnter the currency converter API key (optional): ")
        github = input("\nEnter the link to the GitHub repository this is on (optional): ")
        f.write("#!/usr/bin/env python3\n\n\n"
                + "name = \"{}\"\n".format(name)
                + "pwd = \"{}\"\n".format(pwd)
                + "channel = \"{}\"\n".format(channel)
                + "trigger = \"{}\"\n".format(trigger)
                + "oxfordAppId = \"{}\"\n".format(oxfordAppId)
                + "oxfordAppKey = \"{}\"\n".format(oxfordAppKey)
                + "exchangeRateApiKey = \"{}\"\n".format(exchangeRateApiKey)
                + "github = \"{}\"\n".format(github))

import credentials

random.seed(datetime.datetime.now())
oxfordDictionary = dictionary.Oxford(credentials.oxfordAppId, credentials.oxfordAppKey)
if not credentials.name or not credentials.channel or not credentials.trigger:
    sys.exit("Make sure you have entered \"name\", \"channel\" and \"trigger\" in the file credentials.py.")


def identical_item(list1, list2):
    """Returns the element common to both <list1> (list) as well as <list2> (list) else <None>."""
    for item in list1:
        for part in list2:
            if item == part:
                return item
    return


def callback(hackChat, info):
    """This is an impure callback function that receives and sends data from and to https://hack.chat."""
    if info["type"] == "warn":
        print("\nWARNING at {}:\n{}".format(datetime.datetime.now(), info["warning"]))
    elif info["type"] == "invite":
        connection.HackChat(callback, credentials.name, credentials.pwd).join(info["channel"])
    elif info["type"] == "stats":
        hackChat.send("There are {} unique IPs in {} channels.".format(info["IPs"], info["channels"]))
    if info["type"] != "message":
        return
    isCmd = lambda cmd: info["text"][:len(credentials.trigger + cmd)].lower() == "{}{}".format(credentials.trigger, cmd)
    space = re.search(r"\s", info["text"].strip())
    if isCmd("about") and credentials.github:
        hackChat.send("@{} {}".format(info["nick"], credentials.github))
    elif isCmd("define") and credentials.oxfordAppId and credentials.oxfordAppKey:
        if space:
            data = oxfordDictionary.define(info["text"][space.end():])
            if type(data) is str:
                hackChat.send("@{} {}: {}".format(info["nick"], info["text"][space.end():], data))
            else:
                hackChat.send("@{} Sorry, I couldn't find any definitions for that.".format(info["nick"]))
        else:
            hackChat.send("@{} (e.g., {}define hello)".format(info["nick"], credentials.trigger))
    elif (isCmd("h") and len(info["text"].strip()) == len(credentials.trigger + "h")) or isCmd("help"):
        commands = ["about", "h", "help", "join", "joke", "katex", "poem", "poet", "password", "search", "stats",
                    "toss", "urban"]
        if credentials.oxfordAppId and credentials.oxfordAppKey:
            commands += ["define", "translate"]
        if credentials.exchangeRateApiKey:
            commands.append("rate")
        reply = " {}".format(credentials.trigger).join(sorted(commands))
        hackChat.send("@{} {}{}".format(info["nick"], credentials.trigger, reply))
    elif isCmd("join"):
        if space:
            connection.HackChat(callback, credentials.name, credentials.pwd).join(info["text"][space.end():])
        else:
            hackChat.send("@{} joins a hack.chat channel (e.g., {}join ben)\n".format(info["nick"], credentials.trigger)
                          + "You can also invite the bot via the sidebar.")
    elif isCmd("joke"):
        hackChat.send("@{} {}".format(info["nick"], jokes.yo_momma()))
    elif isCmd("katex"):
        colors = ["red", "orange", "green", "blue", "pink", "purple", "gray", "rainbow"]
        sizes = ["tiny", "scriptsize", "footnotesize", "small", "normalsize", "large", "Large", "LARGE", "huge", "Huge"]
        fonts = ["mathrm", "mathit", "mathbf", "mathsf", "mathtt", "mathbb", "mathcal", "mathfrak", "mathscr"]
        if space:
            msg = info["text"][space.end():]
            if set(msg).isdisjoint(("#", "$", "%", "&", "_", "{", "}", "\\", "?")):
                data = info["text"][:space.start()].split(".")
                stringify = lambda value: value if value else ""
                size = stringify(identical_item(data, sizes))
                color = stringify(identical_item(data, colors))
                font = stringify(identical_item(data, fonts))
                hackChat.send("@{} says {}".format(info["nick"], katex.katex_generator(msg, size, color, font)))
            else:
                hackChat.send("@%s KaTeX doesn't support \"?\", \"{\", \"}\", \"\\\" and \"_\"" % info["nick"])
        else:
            reply = "@{} stylizes text (e.g., {}katex.rainbow.huge hello)\n".format(info["nick"], credentials.trigger)
            optional = lambda x: "\", \"".join(x)
            reply += "OPTIONAL COLORS: \"{}\"\n".format(optional(colors))
            reply += "OPTIONAL SIZES: \"{}\"\n".format(optional(sizes))
            reply += "OPTIONAL FONTS: \"{}\"\n".format(optional(fonts))
            hackChat.send(reply)
    elif isCmd("password"):
        if space:
            hackChat.send("@{} {}".format(info["nick"], password.strengthen(info["text"][space.end():])))
        else:
            hackChat.send("@{} strengthens a password (e.g., {}password gum)".format(info["nick"], credentials.trigger))
    elif isCmd("poem") or isCmd("poet"):
        if space:
            poet = True if info["text"][len(credentials.trigger):len(credentials.trigger + "poet")] == "poet" else False
            data = poetry.poems(info["text"][space.end():], poet)
            if data:
                data = data[random.randint(0, len(data) - 1)]
                poem = ""
                for line in range(0, 3):
                    poem += data["poem"].split("\n")[line] + "\n"
                pastedPoem = paste.dpaste(data["poem"], title = "{} by {}".format(data["title"], data["author"]))
                hackChat.send("@{} {}\nBy: {}\n{}".format(info["nick"], data["title"], data["author"], poem)
                              + "You can read the rest at {}".format(pastedPoem))
            else:
                hackChat.send("@{} Sorry, I couldn't find any poems for that.".format(info["nick"]))
        else:
            if isCmd("poem"):
                hackChat.send("@{} finds a poem by its name ".format(info["nick"])
                              + "(e.g., {}poem sonnet)".format(credentials.trigger))
            else:
                hackChat.send("@{} finds a poem from a poet ".format(info["nick"])
                              + "(e.g., {}poet shakespeare)".format(credentials.trigger))
    elif isCmd("rate") and credentials.exchangeRateApiKey:
        converted = False
        if len(re.findall(":", info["text"])) == 2:
            firstColon = re.search(":", info["text"])
            secondColon = re.search(":", info["text"][firstColon.end():])
            fromCode = info["text"][firstColon.end():firstColon.end() + secondColon.start()]
            toCode = info["text"][firstColon.end() + secondColon.end():firstColon.end() + secondColon.end() + 3]
            if fromCode and toCode:
                rate = currency.convert(credentials.exchangeRateApiKey, fromCode, toCode)
                if type(rate) is float:
                    converted = True
                    hackChat.send("@{} 1 {} = {} {}".format(info["nick"], fromCode.upper(), rate, toCode.upper()))
        if not converted:
            hackChat.send("@{} Sorry, I couldn't convert that. ".format(info["nick"])
                          + "(e.g., {}rate:usd:inr gives 1 USD = 64 INR)".format(credentials.trigger))
    elif isCmd("search"):
        if space:
            results = search.duckduckgo(info["text"][space.end():], "hack.chat bot")
            reply = ""
            if "Answer" in results or "AbstractText" in results:
                if "URL" in results:
                    reply += "{} ".format(results["URL"])
                if "Heading" in results:
                    reply += "{}: ".format(results["Heading"])
                if "Answer" in results:
                    modify = results["Answer"]
                elif "AbstractText" in results:
                    modify = results["AbstractText"]
                modify = modify[:80 * 6][::-1]
                period = re.search("\.", modify)
                reply += modify[period.start():][::-1]
            hackChat.send("@{} {}".format(info["nick"], reply if reply else "Sorry, I couldn't find anything."))
        else:
            hackChat.send("@{} instant answers (e.g., {}search pokemon ruby)".format(info["nick"], credentials.trigger))
    elif isCmd("stats"):
        hackChat.stats()
    elif isCmd("toss"):
        hackChat.send("@{} {}".format(info["nick"], "heads" if random.randint(0, 1) == 1 else "tails"))
    elif isCmd("translate") and credentials.oxfordAppId and credentials.oxfordAppKey:
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
            cmd = info["text"][:space.start()]
            firstColon = re.search(":", cmd)
            secondColon = re.search(":", cmd[firstColon.end():])
            srcLang = cmd[firstColon.end():firstColon.end() + secondColon.start()].lower()
            targetLang = cmd[firstColon.end() + secondColon.end():].lower()
            if srcLang in languages and targetLang in languages:
                srcLang = languages[srcLang]
                targetLang = languages[targetLang]
                words = info["text"][space.end():].split()
                translations = []
                for word in words:
                    lastChar = word[len(word) - 1:]
                    symbol = r"[^a-zA-Z\s]"
                    lastChar = lastChar if re.search(symbol, word) else ""
                    word = re.sub(symbol, "", word)
                    word = oxfordDictionary.translate(word, srcLang, targetLang)
                    if type(word) is not str:
                        translations = []
                        break
                    translations.append(word + lastChar)
                if translations:
                    hackChat.send("@{} {}".format(info["nick"], " ".join(translations)))
                else:
                    hackChat.send("@{} Sorry, I couldn't translate all of that.".format(info["nick"]))
            else:
                translatable = False
        else:
            translatable = False
        if not translatable:
            hackChat.send("@{} supported languages: {}\n".format(info["nick"], ", ".join(languages.keys()))
                          + "e.g., {}translate:english:spanish I have a holiday!\n".format(credentials.trigger)
                          + "will translate from from English to Spanish")
    elif isCmd("urban"):
        if space:
            data = dictionary.urban(info["text"][space.end():])
            if data:
                definition = data["definition"][:80 * 6][::-1]
                if len(data["definition"]) > 80 * 6:
                    space = re.search(r"\s", definition)
                    definition = definition[space.end():]
                definition = definition[::-1]
                hackChat.send("@{} {}: {} {}".format(info["nick"], data["word"], definition, data["permalink"]))
            else:
                hackChat.send("@{} Sorry, I couldn't find any definitions for that.".format(info["nick"]))
        else:
            hackChat.send("@{} searches Urban Dictionary (e.g., {}urban fag)".format(info["nick"], credentials.trigger))


if __name__ == "__main__":
    connection.HackChat(callback, credentials.name, credentials.pwd).join(credentials.channel)
    print("\nThe bot has started.")
