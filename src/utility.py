#!/usr/bin/env python3

"""Contains miscellaneous functions for use in the bot."""

import re


def shorten(string, maxLen, last):
    """Returns <string> with custom truncation.

    Keyword arguments:
    string -- <str>; the text to shorten
    maxLen -- <int>; the maximum number of characters <string> can be
    last -- <str>; truncates <string> to <last> found closest before
            <maxLen>

    If the length of <string> is shorter than <maxLen>, <string> will be
    returned.

    Example:
    # Shortens <sentence> to the <"."> found just before 45 characters
    # giving <"Hi everyone! My name is Indiana Jones.">
    sentence = "Hi everyone! My name is Indiana Jones. How are you?"
    shortened = shorten(sentence, 45, ".")
    """
    if len(string) < maxLen:
        return string
    string = string[:maxLen]
    incompatibilities = (".", "^", "$", "*", "+", "?", "(", ")", "[", "]", "{",
                         "\\", "|", "-")
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
    """Gives the first common element found in list1 present in list2.

    Keyword arguments:
    list1 -- <list>
    list2 -- <list>

    Return values:
    If a common element was found, it will return that.
    If no common element was found, <None> will be returned.
    """
    for item in list1:
        for part in list2:
            if item == part:
                return item
