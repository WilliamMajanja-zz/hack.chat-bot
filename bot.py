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

from commands import get_poem, katex, password, quotes, youtube


if not os.path.isfile("credentials.py"):
    with open("credentials.py", "w") as f:
        print("You can change your credentials in the file credentials.py.")
        name = input("Enter the name of the bot (mandatory): ")
        print("A trip code is a randomly generated code to verify a user regardless of their nickname.")
        tripCode = input("Enter the trip code (optional): ")
        channel = input("Enter which channel you would like to connect to (mandatory): ")
        trigger = input("Enter the bots trigger (e.g., \".\" will trigger the bot for \".help\") (mandatory): ")
        f.write("#!/usr/bin/env python3\n\n\n" +
                "name = \"{}\"\n".format(name) +
                "tripCode = \"{}\"\n".format(tripCode) +
                "channel = \"{}\"\n".format(channel) +
                "trigger = \"{}\"\n".format(trigger))


import credentials


random.seed(datetime.datetime.now())


class ThreadChannels(threading.Thread):
    """Joins a channel on https://hack.chat (e.g., https://hack.chat/?programming).

    Keyword arguments:
    name -- string; the nickname to be used upon entering the channel
    tripCode -- string; the trip code to be used
    channel -- string; the name of the channel to connect to
    func -- function; the name of the function to handle activities in the channel (e.g., <message_got>)

    Below is an example of how to use this class.
    thread = ThreadChannels("myBot", "secretPassword", "programming", message_got)
    thread.start()
    """

    def __init__(self, name, tripCode, channel, func):
        """This function initializes values."""
        threading.Thread.__init__(self)
        self.name = name
        self.tripCode = tripCode
        self.channel = channel
        self.func = func

    def run(self):
        """This function joins the channel on a new thread."""
        self.join_channel()

    def join_channel(self):
        """This function joins a channel on https://hack.chat."""
        chat = hackchat.HackChat(self.name + "#" + self.tripCode, self.channel)
        chat.on_message.append(self.func)
        chat.start_ping_thread()
        chat.run_loop()


def message_got(chat, message, sender):
    """This is an impure function that checks messages on https://hack.chat and responds to ones triggering the bot."""
    msg = " ".join(message.split())
    space = re.search(r"\s", msg)
    if msg[:1] == credentials.trigger:
        cmd = msg[1:space.start()] if space else msg[1:]
        arg = msg[space.end():] if space else False
        replied = True
        if cmd.lower() == "poem" or cmd.lower() == "poet":
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
        elif cmd.lower() == "h" or cmd.lower() == "help":
            commands = sorted(("about", "h", "help", "yt", "poem", "poet", "toss", "quote", "pwd", "join",
                               "katex<optional_color><optional_size"))
            reply = " {}".format(credentials.trigger).join(commands)
            reply = "." + reply
        elif cmd.lower() == "about":
            reply = ("Creator: Neel Kamath https://github.com/neelkamath\n" +
                     "Code: https://github.com/neelkamath/hack.chat-bot\n" +
                     "Language: Python\n" +
                     "Website: https://neelkamath.github.io\n")
        elif cmd.lower() == "pwd":
            if arg:
                reply = password.strengthen_password(arg)
            else:
                reply = "strengthens a password (e.g., {}pwd mypassword)".format(credentials.trigger)
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
                ThreadChannels(credentials.name, credentials.tripCode, arg, message_got).start()
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


ThreadChannels(credentials.name, credentials.tripCode, credentials.channel, message_got).start()
print("The bot has started...")
