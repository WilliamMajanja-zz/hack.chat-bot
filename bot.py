#!/usr/bin/env python3

"""This file is used to connect the bot to https://hack.chat.

It creates a file named credentials.py containing credentials inputted by the user via the command line if one isn't
found in this directory. It then connects to a channel specified in the file credentials.py on https://hack.chat and
interacts with users triggering it. Its activities are logged in the file activities.log.
"""

import datetime
import random
import threading
import re
import os.path

import hackchat

from commands import dictionary, get_poem, katex, password, quotes, youtube


if not os.path.isfile("credentials.py"):
    with open("credentials.py", "w") as f:
        print("You can change your credentials in the file credentials.py.")
        name = input("Enter the name of the bot: ")
        print("A trip code is a randomly generated code to verify a user regardless of their nickname.")
        password = input("Enter the password for the trip code (optional): ")
        channel = input("Enter which channel you would like to connect to: ")
        trigger = input("Enter the bots trigger (e.g., \".\" will trigger the bot for \".help\"): ")
        oxfordAppId = input("Enter the Oxford Dictionaries API app id: ")
        oxfordAppKey = input("Enter the Oxford Dictionaries API app key: ")
        f.write("#!/usr/bin/env python3\n\n\n" +
                "name = \"{}\"\n".format(name) +
                "password = \"{}\"\n".format(password) +
                "channel = \"{}\"\n".format(channel) +
                "trigger = \"{}\"\n".format(trigger) +
                "oxfordAppId = \"{}\"\n".format(oxfordAppId) +
                "oxfordAppKey = \"{}\"\n".format(oxfordAppKey))


import credentials


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
    msg = " ".join(message.split())
    space = re.search(r"\s", msg)
    if msg[:len(credentials.trigger)] == credentials.trigger:
        cmd = msg[1:space.start()] if space else msg[1:]
        arg = msg[space.end():] if space else False
        replied = True
        if cmd.lower() == "h" or cmd.lower() == "help":
            commands = sorted(("about", "h", "help", "yt", "poem", "poet", "toss", "quote", "password", "join",
                               "katex<optional_color><optional_size>", "define", "translate:<from>:<to>"))
            reply = " {}".format(credentials.trigger).join(commands)
            reply = "." + reply
        elif cmd.lower() == "about":
            reply = ("Creator: Neel Kamath https://github.com/neelkamath\n" +
                     "Code: https://github.com/neelkamath/hack.chat-bot\n" +
                     "Language: Python\n" +
                     "Website: https://neelkamath.github.io\n")
        elif cmd.lower() == "poem" or cmd.lower() == "poet":
            if arg:
                data = get_poem.get_poem(arg, True if cmd == "poet" else False)
                if data == None:
                    reply = "Sorry, I couldn't find any poems for that."
                else:
                    poem = data[0].split("\n")
                    reply = ""
                    for index, line in enumerate(poem):
                        reply += line + "\n"
                        if index == 7:
                            reply += data[1]
                            break
            else:
                if cmd == "poem":
                    reply = "finds a poem by its name (e.g., {}poem daffodils)".format(credentials.trigger)
                else:
                    reply = "finds a poem from a poet (e.g., {}poet shakespeare)".format(credentials.trigger)
        elif cmd[:5].lower() == "katex":
            if arg:
                if "?" in arg or "{" in arg or "}" in arg:
                    reply = "KaTeX doesn't support \"?\", \"{\" and \"}\""
                else:
                    colors = ["red", "orange", "green", "blue", "pink", "purple", "gray", "rainbow"]
                    for color in colors:
                        if color in cmd:
                            break
                        else:
                            color = ""
                    sizes = ["tiny", "scriptsize", "footnotesize", "small", "normalsize", "large", "Large", "LARGE",
                             "huge", "Huge"]
                    for size in sizes:
                        if size in cmd:
                            break
                        else:
                            size = ""
                    reply = "says " + katex.katex_generator(arg, size, color)
            else:
                reply = ("stylizes text (e.g., {}katex.rainbow.large hello world)\n".format(credentials.trigger) +
                         "optional colors: \"red\", \"orange\", \"green\", \"blue\", \"pink\", \"purple\", \"gray\", " +
                         "\"rainbow\"\n" +
                         "optional sizes: \"tiny\", \"scriptsize\", \"footnotesize\", \"small\", \"normalsize\", " +
                         "\"large\", \"Large\", \"LARGE\", \"huge\", \"Huge\"")
        elif cmd.lower() == "quote":
            if arg:
                data = quotes.quotes(arg)
                if data:
                    reply = data[random.randint(0, len(data) - 1)]
                else:
                    reply = "Sorry, I couldn't find any quotes for that."
            else:
                reply = "gives quotes from people (e.g., {}quote buddha)".format(credentials.trigger)
        elif cmd.lower() == "define":
            if arg:
                data = dictionary.define(arg)
                if data:
                    reply = "{}: {}".format(arg, data)
                else:
                    reply = "Sorry, I couldn't find any definitions for that."
            else:
                reply = "gives a definition (e.g., {}define hello)".format(credentials.trigger)
        elif cmd.lower()[:9] == "translate":
            languages = {"en": "english",
                         "es": "spanish",
                         "nso": "pedi",
                         "ro": "romanian",
                         "ms": "malay",
                         "zu": "zulu",
                         "id": "indonesian",
                         "tn": "tswana"}
            supported = "supported languages: {}".format(", ".join(languages.values()))
            if arg:
                if len(re.findall(":", cmd)) == 2:
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
                        words = arg.split()
                        translations = []
                        translated = True
                        for word in words:
                            lastChar = word[len(word) - 1:]
                            pattern = r"[^a-zA-Z\s]"
                            lastChar = lastChar if re.search(pattern, word) else ""
                            word = re.sub(pattern, "", word)
                            word = dictionary.translate(word, srcLang, targetLang)
                            if word == None:
                                translated = False
                                break
                            translations.append(word + lastChar)
                        reply = " ".join(translations) if translated else "I'm sorry, I couldn't translate all of that."
                    else:
                        reply = supported
                else:
                    reply = ("state the languages (e.g., {}translate:english:espanol)\n".format(credentials.trigger) +
                             "{}".format(supported))
            else:
                reply = ("{}\n".format(supported) +
                         "e.g., {}translate:english:espanol Hello, how are you?\n".format(credentials.trigger) +
                         "will translate from from English to Espanol")
        elif cmd.lower() == "password":
            if arg:
                reply = password.strengthen_password(arg)
            else:
                reply = "strengthens a password (e.g., {}password mypassword)".format(credentials.trigger)
        elif cmd.lower() == "yt":
            if arg:
                count = 0
                videos = youtube.videos(arg)
                if videos:
                    reply = ""
                    for video in videos:
                        reply += video + "\n" + videos[video] + "\n"
                        count += 1
                        if count == 3:
                            break
                else:
                    reply = "Sorry, I couldn't find any videos for that."
            else:
                reply = "searches YouTube (e.g., {}yt star wars trailer)".format(credentials.trigger)
        elif cmd.lower() == "toss":
            reply = "heads" if random.randint(0, 1) == 1 else "tails"
        elif cmd.lower() == "join":
            if arg:
                ThreadChannels(message_got, arg, credentials.name, credentials.password).start()
                replied = False
            else:
                reply = "joins a hack.chat channel (e.g., {}join pokemon)".format(credentials.trigger)
        else:
            replied = False
        if replied:
            reply = "@{} ".format(sender) + reply
            chat.send_message(reply)
            with open("activities.log", "a") as f:
                prettifiedMsg = message.replace("\n", "\n{}".format(" " * len(sender + ": ")))
                prettifiedReply = reply.replace("\n", "\n{}".format(" " * len(credentials.name + ": ")))
                f.write(sender + ": " + prettifiedMsg + "\n" + credentials.name + ": " + prettifiedReply + "\n")


ThreadChannels(message_got, credentials.channel, credentials.name, credentials.password).start()
dictionary = dictionary.Dictionary(credentials.oxfordAppId, credentials.oxfordAppKey)
print("The bot has started.")
