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
        print("You can change your credentials later in the file credentials.py located in the src folder. The " +
              "features whose API tokens you don't enter will remain inaccessible until you enter them.")
        name = input("Enter the name of the bot (e.g., myBot) (mandatory): ")
        print("\nA trip code is a randomly generated code based on a password. Entering the same password gives the " +
              "same trip code each time. This allows people in anonymous chatting sites to verify if a user is who " +
              "they claim to be regardless of their nickname.")
        pwd = getpass.getpass("Enter the password for the trip code (e.g., myPassword) (optional): ")
        print("\nChannels are chats on https://hack.chat. If the channel for the name you enter doesn't exist, one " +
              "will automatically be created. To join the \"math\" channel (https://hack.chat/?math), enter \"math\".)")
        channel = input("Enter which channel you would like to connect to (mandatory): ")
        print("\nFor the bot to know when it's being called, you must state a trigger.")
        trigger = input("Enter the bots trigger (e.g., \".\" will trigger the bot for \".help\") (mandatory): ")
        oxfordAppId = input("\nEnter the Oxford Dictionaries API app id for definitions and translations (optional): ")
        oxfordAppKey = input("Enter the Oxford Dictionaries API app key for definitions and translations (optional): ")
        exchangeRateApiKey = input("\nEnter the currency converter API key (optional): ")
        github = input("\nEnter the link to the GitHub repository this is on (optional): ")
        f.write("#!/usr/bin/env python3\n\n\n" +
                "name = \"{}\"\n".format(name) +
                "pwd = \"{}\"\n".format(pwd) +
                "channel = \"{}\"\n".format(channel) +
                "trigger = \"{}\"\n".format(trigger) +
                "oxfordAppId = \"{}\"\n".format(oxfordAppId) +
                "oxfordAppKey = \"{}\"\n".format(oxfordAppKey) +
                "exchangeRateApiKey = \"{}\"\n".format(exchangeRateApiKey) +
                "github = \"{}\"\n".format(github))

import credentials

if not credentials.name or not credentials.channel or not credentials.trigger:
    sys.exit("Make sure you have entered \"name\", \"channel\" and \"trigger\" in the file credentials.py.")
random.seed(datetime.datetime.now())


class ThreadChannels(threading.Thread):
    """This is an impure class that runs an instance of a bot on https://hack.chat.

    Keyword arguments:
    callback -- function; the name of the callback function to receive data from https://hack.chat
    channel -- string; the channel to connect to
    nick -- the nickname of the bot
    pwd -- the password used to generate a tripcode on the site

    Example:
    thread = ThreadChannels(on_message, "botDev", "myBot")
    thread.start()
    """

    def __init__(self, callback, channel, nick, pwd = ""):
        """This function initializes the values."""
        threading.Thread.__init__(self)
        self.callback = callback
        self.channel = channel
        self.nick = nick
        self.pwd = pwd

    def run(self):
        """Accessing the <start> function in turn accesses this <run> function to start the thread."""
        connector = connection.HackChat(self.callback, self.channel, self.nick, self.pwd)


def on_message(chat, info):
    """This is an impure callback function that receives and sends data to a channel on https://hack.chat."""
    if info["type"] == "warn":
        print("\nWARNING:\n{}\n".format(info["warning"]))
    elif info["type"] == "invite":
        ThreadChannels(on_message, info["channel"], credentials.name, credentials.pwd).start()
    elif info["type"] == "stats":
        chat.send("There are {} unique IPs in {} channels.".format(info["IPs"], info["channels"]))
    if info["type"] != "message":
        return
    if (info["text"][:len(credentials.trigger + "about")].lower() == "{}about".format(credentials.trigger) and
        credentials.github):
        chat.send("@{} {}".format(info["nick"], credentials.github))
    elif (info["text"][:len(credentials.trigger + "define")].lower() == "{}define".format(credentials.trigger) and
          credentials.oxfordAppId and credentials.oxfordAppKey):
        space = re.search(r"\s", info["text"].strip())
        if space:
            data = oxfordDictionary.define(info["text"][space.end():])
            if type(data) is str:
                chat.send("@{} {}: {}".format(info["nick"], info["text"][space.end():], data))
            else:
                chat.send("@{} Sorry, I couldn't find any definitions for that.".format(info["nick"]))
        else:
            chat.send("@{} e.g., {}define hello".format(info["nick"], credentials.trigger))
    elif ((info["text"][:len(credentials.trigger + "h")].lower() == "{}h".format(credentials.trigger) and
           len(info["text"].strip()) == len(credentials.trigger + "h")) or
          info["text"][:len(credentials.trigger + "help")].lower() == "{}help".format(credentials.trigger)):
        commands = ["about", "h", "help", "join", "joke", "katex", "poem", "poet", "password", "search", "stats",
                    "toss", "urban"]
        if credentials.oxfordAppId and credentials.oxfordAppKey:
            commands += ["define", "translate"]
        if credentials.exchangeRateApiKey:
            commands.append("rate")
        reply = " {}".format(credentials.trigger).join(sorted(commands))
        chat.send("@{} {}{}".format(info["nick"], credentials.trigger, reply))
    elif info["text"][:len(credentials.trigger + "join")].lower() == "{}join".format(credentials.trigger):
        space = re.search(r"\s", info["text"].strip())
        if space:
            ThreadChannels(on_message, info["text"][space.end():], credentials.name, credentials.pwd).start()
        else:
            chat.send("@{} joins a hack.chat channel (e.g., {}join math)\n".format(info["nick"], credentials.trigger) +
                      "You can also invite the bot via the sidebar.")
    elif info["text"][:len(credentials.trigger + "joke")].lower() == "{}joke".format(credentials.trigger):
        chat.send("@{} {}".format(info["nick"], jokes.yo_momma()))
    elif info["text"][:len(credentials.trigger + "katex")].lower() == "{}katex".format(credentials.trigger):
        space = re.search(r"\s", info["text"].strip())
        if space:
            txt = info["text"][space.end():]
            if "?" in txt or "{" in txt or "}" in txt or "\\" in txt or "_" in txt:
                chat.send("@%s KaTeX doesn't support \"?\", \"{\", \"}\", \"\\\" and \"_\"" % info["nick"])
            else:
                colors = ["red", "orange", "green", "blue", "pink", "purple", "gray", "rainbow"]
                for color in colors:
                    if color in info["text"][:space.start()]:
                        break
                    else:
                        color = ""
                sizes = ["tiny", "scriptsize", "footnotesize", "small", "normalsize", "large", "Large", "LARGE", "huge",
                         "Huge"]
                for size in sizes:
                    if size in info["text"][:space.start()]:
                        break
                    else:
                        size = ""
                chat.send("@{} says {}".format(info["nick"], katex.katex_generator(txt, size, color)))
        else:
            chat.send("@{} stylizes text ".format(info["nick"]) +
                              "(e.g., {}katex.rainbow.large hello world)\n".format(credentials.trigger) +
                              "optional colors: \"red\", \"orange\", \"green\", \"blue\", \"pink\", \"purple\", " +
                              "\"gray\", \"rainbow\"\n" +
                              "optional sizes: \"tiny\", \"scriptsize\", \"footnotesize\", \"small\", " +
                              "\"normalsize\", \"large\", \"Large\", \"LARGE\", \"huge\", \"Huge\"")
    elif info["text"][:len(credentials.trigger + "password")].lower() == "{}password".format(credentials.trigger):
        space = re.search(r"\s", info["text"].strip())
        if space:
            chat.send("@{} {}".format(info["nick"], password.strengthen_password(info["text"][space.end():])))
        else:
            chat.send("@{} strengthens a password (e.g., {}password test)".format(info["nick"], credentials.trigger))
    elif (info["text"][:len(credentials.trigger + "poem")].lower() == "{}poem".format(credentials.trigger) or
          info["text"][:len(credentials.trigger + "poet")].lower() == "{}poet".format(credentials.trigger)):
        space = re.search(r"\s", info["text"].strip())
        if space:
            if info["text"][len(credentials.trigger):len(credentials.trigger + "poet")] == "poet":
                isAuthor = True
            else:
                isAuthor = False
            data = poetry.poems(info["text"][space.end():], isAuthor)
            if data:
                data = data[random.randint(0, len(data) - 1)]
                poem = ""
                for line in range(0, 3):
                    poem += data["poem"].split("\n")[line] + "\n"
                pastedPoem = paste.dpaste(data["poem"], title = "{} by {}".format(data["title"], data["author"]))
                chat.send("@{} {}\nBy: {}\n{}".format(info["nick"], data["title"], data["author"], poem) +
                                  "You can read the rest at {}".format(pastedPoem))
            else:
                chat.send("@{} Sorry, I couldn't find any poems for that.".format(info["nick"]))
        else:
            if info["text"][len(credentials.trigger):len(credentials.trigger + "poem")].lower() == "poem":
                chat.send("@{} finds a poem by its name ".format(info["nick"]) +
                                  "(e.g., {}poem daffodils)".format(credentials.trigger))
            elif info["text"][len(credentials.trigger):len(credentials.trigger + "poet")].lower() == "poet":
                chat.send("@{} finds a poem from a poet ".format(info["nick"]) +
                                  "(e.g., {}poet shakespeare)".format(credentials.trigger))
    elif (info["text"][:len(credentials.trigger + "rate")].lower() == "{}rate".format(credentials.trigger) and
          credentials.exchangeRateApiKey):
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
                    chat.send("@{} 1 {} = {} {}".format(info["nick"], fromCode.upper(), rate, toCode.upper()))
        if not converted:
            chat.send("@{} Sorry, I couldn't convert that. ".format(info["nick"]) +
                              "(e.g., {}rate:usd:inr gives 1 USD = 64 INR)".format(credentials.trigger))
    elif info["text"][:len(credentials.trigger + "search")].lower() == "{}search".format(credentials.trigger):
        space = re.search(r"\s", info["text"])
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
                modify = modify.split(". ")
                modified = ""
                count = 0
                for sentence in modify:
                    count += len(sentence)
                    if count > 80 * 6:
                        reply += modified
                        break
                    modified += "{}. ".format(sentence)
            chat.send("@{} {}".format(info["nick"], reply if reply else "Sorry, I couldn't find anything."))
        else:
            chat.send("@{} instant answers (e.g., {}search pokemon black)".format(info["nick"], credentials.trigger))
    elif info["text"][:len(credentials.trigger + "stats")].lower() == "{}stats".format(credentials.trigger):
        chat.stats()
    elif info["text"][:len(credentials.trigger + "toss")].lower() == "{}toss".format(credentials.trigger):
        chat.send("@{} {}".format(info["nick"], "heads" if random.randint(0, 1) == 1 else "tails"))
    elif (info["text"][:len(credentials.trigger + "translate")].lower() == "{}translate".format(credentials.trigger) and
          credentials.oxfordAppId and credentials.oxfordAppKey):
        languages = {"en": "english",
                     "es": "spanish",
                     "nso": "pedi",
                     "ro": "romanian",
                     "ms": "malay",
                     "zu": "zulu",
                     "id": "indonesian",
                     "tn": "tswana"}
        space = re.search(r"\s", info["text"].strip())
        translatable = True
        if space and len(re.findall(":", info["text"][:space.start()])) == 2:
            cmd = info["text"][:space.start()]
            firstColon = re.search(":", cmd)
            secondColon = re.search(":", cmd[firstColon.end():])
            srcLang = cmd[firstColon.end():firstColon.end() + secondColon.start()].lower()
            targetLang = cmd[firstColon.end() + secondColon.end():].lower()
            if srcLang in languages.values() and targetLang in languages.values():
                for language in languages:
                    if srcLang == languages[language]:
                        srcLang = language
                    if targetLang == languages[language]:
                        targetLang = language
                words = info["text"][space.end():].split()
                translations = []
                for word in words:
                    lastChar = word[len(word) - 1:]
                    pattern = r"[^a-zA-Z\s]"
                    lastChar = lastChar if re.search(pattern, word) else ""
                    word = re.sub(pattern, "", word)
                    word = oxfordDictionary.translate(word, srcLang, targetLang)
                    if type(word) is not str:
                        translations = []
                        break
                    translations.append(word + lastChar)
                if translations:
                    chat.send("@{} {}".format(info["nick"], " ".join(translations)))
                else:
                    chat.send("@{} Sorry, I couldn't translate all of that.".format(info["nick"]))
            else:
                translatable = False
        else:
            translatable = False
        if not translatable:
            chat.send("@{} supported languages: {}\n".format(info["nick"], ", ".join(languages.values())) +
                              "e.g., {}translate:english:spanish I have a holiday!\n".format(credentials.trigger) +
                              "will translate from from English to Spanish")
    elif info["text"][:len(credentials.trigger + "urban")].lower() == "{}urban".format(credentials.trigger):
        space = re.search(r"\s", info["text"].strip())
        if space:
            data = dictionary.urban_dictionary(info["text"][space.end():])
            if data:
                words = data["definition"].split()
                definition = ""
                length = 0
                for word in words:
                    definition += word + " "
                    if len(definition) > 80 * 6:
                        break
                chat.send("@{} {}: {} {}".format(info["nick"], data["word"], definition, data["permalink"]))
            else:
                chat.send("@{} Sorry, I couldn't find any definitions for that.".format(info["nick"]))
        else:
            chat.send("@{} searches Urban Dictionary (e.g., {}urban swag)".format(info["nick"], credentials.trigger))


if __name__ == "__main__":
    oxfordDictionary = dictionary.OxfordDictionary(credentials.oxfordAppId, credentials.oxfordAppKey)
    ThreadChannels(on_message, credentials.channel, credentials.name, credentials.pwd).start()
    print("\nThe bot has started.")
