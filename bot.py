#!/usr/bin/env python3

import datetime
import random
import threading
import re
import os.path

import hackchat

from commands import get_poem, katex, password, quotes, youtube


if not os.path.isfile("credentials.py"):
    print("You can change your credentials later in the file credentials.py located in the root directory of this bot.")
    with open("credentials.py", "w") as f:
        name = input("Enter the name of the bot: ")
        print("A trip code is a randomly generated code to verify a user is the same regardless of their nickname.")
        tripCode = input("Enter the trip code or leave it blank if you don't want to use one yet: ")
        channel = input("Enter which channel you would like to connect to: ")
        trigger = input("Enter what will trigger the bot (e.g., entering \".\" will trigger the bot for \".help\"): ")
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
    msg = message.strip()
    space = re.search(r"\s", msg)
    if msg[:1] == trigger:
        cmd = msg[1:space.start()] if space else msg[1:]
        cmd = cmd.lower()
        arg = msg[space.end():] if space else False
        valid = True
        if cmd == "poem" or cmd == "poet":
            if arg:
                data = get_poem.get_poem(arg, True if cmd == "poet" else False)
                if data == None:
                    reply = "Sorry, I couldn't find any poems for that."
                else:
                    poem = data[0].split("\n")
                    lines = 0
                    reply = ""
                    for line in poem:
                        reply += line + "\n"
                        lines += 1
                        if lines == 7:
                            reply += data[1]
                            break
            else:
                if cmd == "poem":
                    reply = "finds a poem by its name (e.g., {}poem daffodils)".format(trigger)
                else:
                    reply = "finds a poem from a poet (e.g., {}poet shakespeare)".format(trigger)
        elif cmd[:5] == "katex":
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
                reply = ("stylizes text (e.g., {}katex.rainbow.large hello world)\n".format(trigger) +
                         "optional colors: \"red\", \"orange\", \"green\", \"blue\", \"pink\", \"purple\", \"gray\", " +
                         "\"rainbow\"\n" +
                         "optional sizes: \"tiny\", \"scriptsize\", \"footnotesize\", \"small\", \"normalsize\", " +
                         "\"large\", \"Large\", \"LARGE\", \"huge\", \"Huge\"")
        elif cmd == "quote":
            if arg:
                data = quotes.quotes(arg)
                if data:
                    reply = data[random.randint(0, len(data) - 1)]
                else:
                    reply = "Sorry, I couldn't find any quotes for that."
            else:
                reply = "gives quotes from people (e.g., {}quote buddha)".format(trigger)
        elif cmd == "h" or cmd == "help":
            commands = sorted(("about", "h", "help", "yt", "poem", "poet", "toss", "quote", "pwd", "join",
                               "katex<optional_color><optional_size"))
            reply = ""
            for cmd in commands:
                reply += " " + trigger + cmd
            reply = reply[1:]
        elif cmd == "about":
            reply = ("Creator: Neel Kamath https://github.com/neelkamath\n" +
                     "Code: https://github.com/neelkamath/hack.chat-bot\n" +
                     "Language: Python\n" +
                     "Website: https://neelkamath.github.io\n")
        elif cmd == "pwd":
            if arg:
                reply = password.strengthen_password(arg)
            else:
                reply = "strengthens a password (e.g., {}pwd mypassword)".format(trigger)
        elif cmd == "yt":
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
                reply = "searches YouTube (e.g., {}yt star wars trailer)".format(trigger)
        elif cmd == "toss":
            reply = "heads" if random.randint(0, 1) == 1 else "tails"
        elif cmd == "join":
            if arg:
                ThreadChannels(name, tripCode, arg, message_got).start()
                reply = "I joined the channel \"{}\".".format(arg)
            else:
                reply = "joins a hack.chat channel (e.g., {}join pokemon)".format(trigger)
        else:
            valid = False
        if valid:
            reply = "@{} ".format(sender) + reply
            chat.send_message(reply)
            with open("activities.log", "a") as f:
                prettifiedMsg = message.replace("\n", "\n{}".format(" " * len(sender + ": ")))
                prettifiedReply = reply.replace("\n", "\n{}".format(" " * len(credentials.name + ": ")))
                f.write(sender + ": " + prettifiedMsg + "\n" + credentials.name + ": " + prettifiedReply + "\n")


name = credentials.name
tripCode = credentials.tripCode
channel = credentials.channel
trigger = credentials.trigger
ThreadChannels(name, tripCode, channel, message_got).start()
print("The bot has started...")
