#!/usr/bin/env python3

import datetime
import random
import re

import hackchat

from commands import info, youtube


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


chat.on_message.append(message_got)
chat.start_ping_thread()
chat.run_loop()
