#!/usr/bin/env python3

import datetime
import random
import re

import hackchat

from commands import info, youtube
from commands.poem_web_scraper import get_poem


random.seed(datetime.datetime.now())
chat = hackchat.HackChat("neelkamath_bot", "programming")


def message_got(chat, message, sender):
    trigger = "."
    msg = message.strip().lower()
    space = re.search(r"\s", msg)
    if msg[:1] == trigger:
        cmd = msg[1:space.start()] if space else msg[1:]
        search = msg[space.end():] if space else False
        if cmd == "h" or cmd == "help":
            chat.send_message(info.commands(trigger))
        elif cmd == "about":
            chat.send_message(info.about())
        elif cmd == "yt":
            if search:
                reply = ""
                count = 0
                videos = youtube.videos(search)
                for video in videos:
                    reply += video + "\n" + videos[video] + "\n"
                    count += 1
                    if count == 3:
                        break
            else:
                reply = "e.g. {}yt star wars trailer".format(trigger)
            chat.send_message(reply)
        elif cmd == "poem" or cmd == "poet":
            if search:
                data = get_poem.get_poem(search, True if cmd == "poem" else False, site = True)
                if data == None:
                    reply = "Sorry, I couldn't find a poem for that."
                else:
                    poem = data[0].split("\n")
                    lines = 0
                    reply = ""
                    for line in poem:
                        reply += line + "\n"
                        lines += 1
                        if lines == 6:
                            reply += "hack.chat won't let me post more but you can read the rest at:\n" + data[1]
                            break
            else:
                reply = "e.g. " + trigger
                reply += "poem daffodils" if cmd == "poem" else "poet shakespeare"
            chat.send_message(reply)


chat.on_message.append(message_got)
chat.start_ping_thread()
chat.run_loop()
