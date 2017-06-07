#!/usr/bin/env python3

"""Contains miscellaneous functions for use in the bot."""

import re


def shorten(string, maxLen, last):
    """Returns <string> with custom truncation.

    Keyword arguments:
    string -- <str>; the text to shorten
    maxLen -- <int>; the maximum number of characters <string> can be
    last -- <str>; truncates <string> to <last> found closest before
            <maxLen> if <maxLen> is less than the length of <string>

    Example:
    # Shortens <sentence> to the <"."> found just before 45 characters
    # giving <"Hi everyone! My name is Indiana Jones.">
    sentence = "Hi everyone! My name is Indiana Jones. How are you?"
    shortened = shorten(sentence, 45, ".")
    """
    if len(string) <= maxLen:
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


def shorten_lines(string, lineLen, maxLines):
    """Truncates <string> to a certain number of lines.

    Keyword arguments:
    string -- <str>; the <str> to shorten
    lineLen -- <int>; the number of characters that constitute one line
    maxLines -- <int>; the number of lines <string> can be at most
    """
    lines = string.split("\n")
    lineCount = 0
    newLines = ""
    for line in lines:
        length = int(len(line) / lineLen) if len(line) > lineLen else 1
        if len(line) > length * lineLen:
            length += 1
        lineCount += length
        if lineCount > maxLines:
            break
        newLines += "{}\n".format(line)
    return newLines


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
