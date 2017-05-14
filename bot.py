#!/usr/bin/env python3

"""This is used to connect the bot to https://hack.chat using credentials from the file credentials.py.

For API-specific features, it checks if the API tokens exist and only then exhibits that functionality.
"""

import datetime
import random
import threading
import re
import os.path
import sys

import hackchat

from commands import currency, dictionary, get_poem, katex, password, quotes, youtube

if not os.path.isfile("credentials.py"):
    with open("credentials.py", "w") as f:
        print("You can change your credentials in the file credentials.py. The features whose API tokens you don't " +
              "enter will remain inaccessible until you enter them.")
        name = input("Enter the name of the bot (mandatory): ")
        print("A trip code is a randomly generated code to verify a user regardless of their nickname.")
        password = input("Enter the password for the trip code (optional): ")
        channel = input("Enter which channel you would like to connect to (mandatory): ")
        trigger = input("Enter the bots trigger (e.g., \".\" will trigger the bot for \".help\") (mandatory): ")
        oxfordAppId = input("Enter the Oxford Dictionaries API app id (optional): ")
        oxfordAppKey = input("Enter the Oxford Dictionaries API app key (optional): ")
        exchangeRateApiKey = input("Enter the currency converter API key (optional): ")
        f.write("#!/usr/bin/env python3\n\n\n" +
                "name = \"{}\"\n".format(name) +
                "password = \"{}\"\n".format(password) +
                "channel = \"{}\"\n".format(channel) +
                "trigger = \"{}\"\n".format(trigger) +
                "oxfordAppId = \"{}\"\n".format(oxfordAppId) +
                "oxfordAppKey = \"{}\"\n".format(oxfordAppKey) +
                "exchangeRateApiKey = \"{}\"\n".fomrat(exchangerateApiKey))

import credentials

if not credentials.name or not credentials.channel or not credentials.trigger:
    sys.exit("Make sure you have entered \"name\", \"channel\" and \"trigger\" in the file credentials.py.")
random.seed(datetime.datetime.now())


class ThreadChannels(threading.Thread):
    """Joins a channel on https://hack.chat (e.g., https://hack.chat/?programming).

    Keyword arguments:
    func -- function; the name of the function to handle activities in the channel (e.g., <message_got>)
    channel -- string; the name of the channel to connect to
    name -- string; the nickname to be used upon entering the channel
    password -- optional string; the password that gives a trip code to be used

    Below is an example of how to use this class.
    thread = ThreadChannels(message_got, "programming", "myBot", "secretPassword")
    thread.start()
    """

    def __init__(self, func, channel, name, password = ""):
        """This function initializes values."""
        threading.Thread.__init__(self)
        self.func = func
        self.channel = channel
        self.name = name
        self.password = password

    def run(self):
        """This function joins the channel on a new thread."""
        self.join_channel()

    def join_channel(self):
        """This function joins a channel on https://hack.chat."""
        chat = hackchat.HackChat(self.name + "#" + self.password, self.channel)
        chat.on_message.append(self.func)
        chat.start_ping_thread()
        chat.run_loop()


def message_got(chat, message, sender):
    """This is an impure function that checks messages on https://hack.chat and responds to ones triggering the bot."""
    if message[:len(credentials.trigger + "about")].lower() == "{}about".format(credentials.trigger):
        chat.send_message("@{} Creator: Neel Kamath https://github.com/neelkamath\n".format(sender) +
                          "Code: https://github.com/neelkamath/hack.chat-bot\n" +
                          "Language: Python\n" +
                          "Website: https://neelkamath.github.io\n")
    elif (message[:len(credentials.trigger + "rate")].lower() == "{}rate".format(credentials.trigger) and
          credentials.exchangeRateApiKey):
        converted = False
        if len(re.findall(":", message)) == 2:
            firstColon = re.search(":", message)
            secondColon = re.search(":", message[firstColon.end():])
            fromCode = message[firstColon.end():firstColon.end() + secondColon.start()]
            toCode = message.strip()[firstColon.end() + secondColon.end():]
            if fromCode and toCode:
                rate = currency.convert(credentials.exchangeRateApiKey, fromCode, toCode)
                if type(rate) is float:
                    converted = True
                    chat.send_message("@{} 1 {} = {} {}".format(sender, fromCode.upper(), rate, toCode.upper()))
        if not converted:
            chat.send_message("@{} Sorry, I couldn't convert that. ".format(sender) +
                              "(e.g., {}rate:usd:inr gives 1 USD = 64 INR)".format(credentials.trigger))
    elif (message[:len(credentials.trigger + "define")].lower() == "{}define".format(credentials.trigger) and
          credentials.oxfordAppId and credentials.oxfordAppKey):
        space = re.search(r"\s", message.strip())
        if space:
            data = dictionary.define(message[space.end():])
            if type(data) is str:
                chat.send_message("@{} {}: {}".format(sender, message[space.end():], data))
            else:
                chat.send_message("@{} Sorry, I couldn't find any definitions for that.".format(sender))
        else:
            chat.send_message("@{} gives a definition (e.g., {}define hello)".format(sender, credentials.trigger))
    elif ((message[:len(credentials.trigger + "h")].lower() == "{}h".format(credentials.trigger) and
           len(message.strip()) == len(credentials.trigger + "h")) or
          message[:len(credentials.trigger + "help")].lower() == "{}help".format(credentials.trigger)):
        commands = ["about", "h", "help", "yt", "poem", "poet", "toss", "quote", "password", "join", "katex"]
        if credentials.oxfordAppId and credentials.oxfordAppKey:
            commands += ["define", "translate"]
        if credentials.exchangeRateApiKey:
            commands.append("rate")
        reply = " {}".format(credentials.trigger).join(sorted(commands))
        chat.send_message("@{} {}{}".format(sender, credentials.trigger, reply))
    elif message[:len(credentials.trigger + "join")].lower() == "{}join".format(credentials.trigger):
        space = re.search(r"\s", message)
        if space:
            ThreadChannels(message_got, message[space.end():], credentials.name, credentials.password).start()
        else:
            chat.send_message("@{} joins a hack.chat channel (e.g., {}join botDev)".format(sender, credentials.trigger))
    elif message[:len(credentials.trigger + "katex")].lower() == "{}katex".format(credentials.trigger):
        space = re.search(r"\s", message.strip())
        if space:
            txt = message[space.end():]
            if "?" in txt or "{" in txt or "}" in txt:
                chat.send_message("@{} KaTeX doesn't support \"?\", \"{\" and \"}\"".format(sender))
            else:
                colors = ["red", "orange", "green", "blue", "pink", "purple", "gray", "rainbow"]
                for color in colors:
                    if color in message[:space.start()]:
                        break
                    else:
                        color = ""
                sizes = ["tiny", "scriptsize", "footnotesize", "small", "normalsize", "large", "Large", "LARGE", "huge",
                         "Huge"]
                for size in sizes:
                    if size in message[:space.start()]:
                        break
                    else:
                        size = ""
                chat.send_message("@{} says {}".format(sender, katex.katex_generator(txt, size, color)))
        else:
            chat.send_message("@{} stylizes text ".format(sender) +
                              "(e.g., {}katex.rainbow.large hello world)\n".format(credentials.trigger) +
                              "optional colors: \"red\", \"orange\", \"green\", \"blue\", \"pink\", \"purple\", " +
                              "\"gray\", \"rainbow\"\n" +
                              "optional sizes: \"tiny\", \"scriptsize\", \"footnotesize\", \"small\", " +
                              "\"normalsize\", \"large\", \"Large\", \"LARGE\", \"huge\", \"Huge\"")
    elif message[:len(credentials.trigger + "password")].lower() == "{}password".format(credentials.trigger):
        space = re.search(r"\s", message.strip())
        if space:
            chat.send_message("@{} {}".format(sender, password.strengthen_password(message[space.end():])))
        else:
            chat.send_message("@{} strengthens a password (e.g., {}password test)".format(sender, credentials.trigger))
    elif (message[:len(credentials.trigger + "poem")].lower() == "{}poem".format(credentials.trigger) or
          message[:len(credentials.trigger + "poet")].lower() == "{}poet".format(credentials.trigger)):
        space = re.search(r"\s", message.strip())
        if space:
            if message[len(credentials.trigger):len(credentials.trigger + "poet")].lower() == "poet":
                poet = True
            else:
                poet = False
            data = get_poem.get_poem(message[space.end():], poet)
            if data == None:
                chat.send_message("@{} Sorry, I couldn't find any poems for that.".format(sender))
            else:
                poem = data[0].split("\n")
                reply = ""
                for index, line in enumerate(poem):
                    reply += line + "\n"
                    if index == 5:
                        reply += data[1]
                        break
                chat.send_message("@{} {}".format(sender, reply))
        else:
            if message[len(credentials.trigger):len(credentials.trigger + "poem")].lower() == "poem":
                chat.send_message("@{} finds a poem by its name ".format(sender) +
                                  "(e.g., {}poem daffodils)".format(credentials.trigger))
            elif message[len(credentials.trigger):len(credentials.trigger + "poet")].lower() == "poet":
                chat.send_message("@{} finds a poem from a poet ".format(sender) +
                                  "(e.g., {}poet shakespeare)".format(credentials.trigger))
    elif message[:len(credentials.trigger + "quote")].lower() == "{}quote".format(credentials.trigger):
        space = re.search(r"\s", message.strip())
        if space:
            data = quotes.quotes(message[:space.start()])
            if data:
                chat.send_message("@{} {}".format(sender, data[random.randint(0, len(data) - 1)]))
            else:
                chat.send_message("@{} Sorry, I couldn't find any quotes for that.".format(sender))
        else:
            chat.send_message("@{} gives quotes from people (e.g., {}quote buddha)".format(sender, credentials.trigger))
    elif message[:len(credentials.trigger + "toss")].lower() == "{}toss".format(credentials.trigger):
        chat.send_message("@{} {}".format(sender, "heads" if random.randint(0, 1) == 1 else "tails"))
    elif (message[:len(credentials.trigger + "translate")].lower() == "{}translate".format(credentials.trigger) and
          credentials.oxfordAppId and credentials.oxfordAppKey):
        languages = {"en": "english",
                     "es": "spanish",
                     "nso": "pedi",
                     "ro": "romanian",
                     "ms": "malay",
                     "zu": "zulu",
                     "id": "indonesian",
                     "tn": "tswana"}
        space = re.search(r"\s", message.strip())
        translatable = True
        if space and len(re.findall(":", message[:space.start()])) == 2:
            cmd = message[:space.start()]
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
                words = message[space.end():].split()
                translations = []
                for word in words:
                    lastChar = word[len(word) - 1:]
                    pattern = r"[^a-zA-Z\s]"
                    lastChar = lastChar if re.search(pattern, word) else ""
                    word = re.sub(pattern, "", word)
                    word = dictionary.translate(word, srcLang, targetLang)
                    if type(word) is not str:
                        translations = []
                        break
                    translations.append(word + lastChar)
                if translations:
                    chat.send_message("@{} {}".format(sender, " ".join(translations)))
                else:
                    chat.send_message("@{} Sorry, I couldn't translate all of that.".format(sender))
            else:
                translatable = False
        else:
            translatable = False
        if not translatable:
            chat.send_message("@{} supported languages: {}\n".format(sender, ", ".join(languages.values())) +
                              "e.g., {}translate:english:spanish I have a holiday!\n".format(credentials.trigger) +
                              "will translate from from English to Spanish")
    elif message[:len(credentials.trigger + "yt")].lower() == "{}yt".format(credentials.trigger):
        space = re.search(r"\s", message.strip())
        if space:
            count = 0
            videos = youtube.videos(message[space.end():])
            if videos:
                reply = ""
                for video in videos:
                    reply += video + "\n" + videos[video] + "\n"
                    count += 1
                    if count == 3:
                        break
                chat.send_message("@{} {}".format(sender, reply))
            else:
                chat.send_message("@{} Sorry, I couldn't find any videos for that.".format(sender))
        else:
            chat.send_message("@{} searches YouTube (e.g., {}yt batman trailer)".format(sender, credentials.trigger))


if __name__ == "__main__":
    ThreadChannels(message_got, credentials.channel, credentials.name, credentials.password).start()
    dictionary = dictionary.Dictionary(credentials.oxfordAppId, credentials.oxfordAppKey)
    print("The bot has started.")
