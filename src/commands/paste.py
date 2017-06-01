#!/usr/bin/env python3

import requests


def dpaste(content, syntax = "text", title = "", poster = "", expiryDays = 1):
    """Pastes to http://dpaste.com/ and returns the pastes url (str).

    Keyword arguments:
    content -- str; what is to be pasted
    syntax -- str; the language of <content>
    title -- str; the title of the paste
    poster -- str; name or email or nickname
    expiryDays -- int; the number of days before the paste is deleted

    <title> shouldn't have more than 100 characters otherwise the following will be returned.
    <"* Ensure this value has at most 100 characters (it has 103).> will be returned.">
    """
    return requests.post("http://dpaste.com/api/v2/", data = {"content": content,
                                                              "syntax": syntax,
                                                              "title": title,
                                                              "poster": poster,
                                                              "expiry_days": expiryDays}).text
