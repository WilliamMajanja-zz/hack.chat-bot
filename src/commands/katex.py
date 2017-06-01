#!/usr/bin/env python3

import re


def katex_generator(txt, size = "normalsize", color = "", font = ""):
    """Returns a KaTeX formatted string (e.g., passing "hi" will return "${h}{i}$").

    Keyword arguments:
    txt -- str; contains text to be converted to katex
    size -- str; changes the font size of <txt>
    color -- str; changes the color of <txt>
    font -- str; changes the font of <txt>

    Values:
    <txt> shouldn't contain "#", "$", "%", "&", "_", "{", "}", "\", "?" as KaTeX doesn't support them.
    <size> values: "tiny" "scriptsize" "footnotesize" "small" "normalsize" "large" "Large" "LARGE" "huge" "Huge"
    <color> values: "red", "orange", "green", "blue", "pink", "purple", "gray", "rainbow", "" (empty string for white)
    <font> values: "\rm", "\it", "\bf", "\sf", "\tt", "\mathrm", "\mathit", "\mathbf", "\mathsf", "\mathtt", "\mathbb",
                   "\mathcal", "\mathfrak", "\mathscr", "\textrm", "\textit", "\textbf", "\textsf", "\texttt",
                   "\textnormal", "\Bbb", "\bold", "\frak"
    """
    txt = " ".join(txt.split())
    katexColor = "\\{}".format(color) if color != "rainbow" and color != "" else color
    font = "\\{}".format(font) if font else font
    rainbow = ["red", "orange", "green", "blue", "purple", "pink"]
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
    size = "\\{}".format(size) if size else size
    return "${}$".format(size + text)
