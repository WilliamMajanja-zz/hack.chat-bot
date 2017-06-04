#!/usr/bin/env python3

import re


def generator(txt, size="normalsize", color="", font=""):
    """Returns KaTeX formatted <txt> (<str>).

    Keyword arguments:
    txt -- <str>; the text to be converted to katex
    size -- <str>; changes the font size of <txt>
    color -- <str>; changes the color of <txt>
    font -- <str>; changes the font of <txt>

    Values:
    <txt> shouldn't contain "#", "$", "%", "&", "_", "{", "}", "\", "?"
    <size> "tiny", "scriptsize", "footnotesize", "small", "normalsize",
           "large", "Large", "LARGE", "huge", "Huge"
    <color> "red", "orange", "green", "blue", "pink", "purple", "gray",
            "rainbow", "" (empty string for white)
    <font> "\rm", "\it", "\bf", "\sf", "\tt", "\mathrm", "\mathit",
           "\mathbf", "\mathsf", "\mathtt", "\mathbb", "\mathcal",
           "\mathfrak", "\mathscr", "\textrm", "\textit", "\textbf",
           "\textsf", "\texttt", "\textnormal", "\Bbb", "\bold", "\frak"
    """
    if color and color != "rainbow":
        katexColor = "\\{}".format(color)
    else:
        katexColor = color
    if font:
        font = "\\{}".format(font)
    rainbow = ["red", "orange", "green", "blue", "purple", "pink"]
    txt = " ".join(txt.split())
    text = ""
    index = 0
    for char in txt:
        if color == "rainbow" and char != " ":
            katexColor = "\\" + rainbow[index % 6]
        if char == " ":
            text += "\\ "
        else:
            text += "%s%s{%s}" % (font, katexColor, char)
            index += 1
    if size:
        size = "\\{}".format(size)
    return "${}$".format(size + text)
