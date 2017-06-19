#!/usr/bin/env python3

import re


def evaluate(string):
    """Safely evaluates mathematical expressions using an eval.

    Keyword arguments:
    string -- <str>; the mathematical expression

    Returns a number if successful otherwise <None>.
    """
    string = re.sub(r"\s", "", string)
    allowed = [str(i) for i in range(0, 10)]
    allowed += ["+", "-", "*", "/", "%", "(", ")"]
    for char in string:
        if char not in allowed:
            return None
    return eval(string)
