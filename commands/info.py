#!/usr/bin/env python3


def commands(trigger):
    """Returns a string explaining how to use the bot. <trigger> is the string that triggers the bots activities."""
    commands = sorted(("about", "h", "help", "yt", "poem", "poet", "toss", "quote"))
    msg = ""
    for cmd in commands:
        msg += " " + trigger + cmd
    return msg[1:]


about = ("Creator: Neel Kamath https://github.com/neelkamath\n" +
         "Code: https://github.com/neelkamath/hack.chat-bot\n" +
         "Language: Python\n" +
         "Website: https://neelkamath.github.io\n")
