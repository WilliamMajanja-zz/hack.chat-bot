#!/usr/bin/env python3

"""This file contains miscellaneous functions for use in the bot."""

import re


def shorten(string, maxLen, last = ""):
    """Shortens <string> (string) to a maximum length of <maxLen> (int) or to the closest <last> before <maxLen>."""
    string = string[:maxLen]
    if last:
        incompatibilities = (".", "^", "$", "*", "+", "?", "(", ")", "[", "]", "{", "\\", "|", "-")
        newLast = ""
        for char in last:
            newLast += "\\{}".format(char) if char in incompatibilities else char
        string = string[::-1]
        found = re.search(newLast, string)
        if found:
            string = string[found.start():]
        string = string[::-1]
    return string


def identical_item(list1, list2):
    """Returns the element common to both <list1> (list) and <list2> (list) else <None>."""
    for item in list1:
        for part in list2:
            if item == part:
                return item
