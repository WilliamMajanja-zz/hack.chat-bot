#!/usr/bin/env python3

import re


def katex_generator(txt, size, color):
    """Returns a katex formatted string (e.g., passing "hi" will return "${h}{i}$").

    Keyword arguments:
    txt -- string; contains text to be converted to katex
    size -- string; set to "large" for large text, "small" for small text or "" for no change in font size
    color -- string; set to one of "red", "orange", "green", "blue", "pink", "purple", "gray", "rainbow", "" (white)

    "{", "}" and "?" must be avoided in <txt> as katex doesn't support them.
    """

    txt = " ".join(txt.split())
    if color and color != "rainbow":
        katexColor = "\\" + color
    else:
        katexColor = ""
    colors = ["red", "orange", "green", "blue", "purple", "pink"]
    text = ""
    for index, char in enumerate(txt):
        if color == "rainbow":
            katexColor = "\\" + colors[index % 6]
        text += "\\ " if char == " " else  katexColor + "{" + char + "}"
    txt = text
    if size == "small":
        size = "\\small"
    elif size == "large":
        size = "\\large"
    return "${}$".format(size + txt)
