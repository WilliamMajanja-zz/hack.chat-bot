#!/usr/bin/env python3

import re


def katex_generator(txt, size, color):
    """Returns a KaTeX formatted string (e.g., passing "hi" will return "${h}{i}$").

    Keyword arguments:
    txt -- string; contains text to be converted to katex
    size -- string; changes the font size of <txt>
            values: "tiny" "scriptsize" "footnotesize" "small" "normalsize" "large" "Large" "LARGE" "huge" "Huge"
    color -- string; changes the color of <txt>
             values: "red", "orange", "green", "blue", "pink", "purple", "gray", "rainbow", "" (empty string for white)

    "{", "}" and "?" must be avoided in <txt> as KaTeX doesn't support them.
    """

    txt = " ".join(txt.split())
    if color and color != "rainbow":
        katexColor = "\\" + color
    else:
        katexColor = ""
    colors = ["red", "orange", "green", "blue", "purple", "pink"]
    text = ""
    index = 0
    for char in txt:
        if color == "rainbow":
            katexColor = "\\" + colors[index % 6]
        if char == " ":
            text += "\\ "
        else:
            text += katexColor + "{" + char + "}"
            index += 1
    txt = text
    size = "\\" + size if size else size
    return "${}$".format(size + txt)
