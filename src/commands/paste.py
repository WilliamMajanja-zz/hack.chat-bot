#!/usr/bin/env python3

import requests


def dpaste(content, syntax="text", title="", poster="", expiryDays=1):
    """Pastes to http://dpaste.com/ and returns the pastes' URL (<str>).

    Keyword arguments:
    content -- <str>; the content to be pasted
    syntax -- <str>; the language of <content>
    title -- <str>; the title of the paste
    poster -- <str>; the name/email/nickname of creator
    expiryDays -- <int>; the number of days before the paste is deleted

    Values:
    <syntax> may be one of those listed at
             http://dpaste.com/api/v2/syntax-choices/
    <title> should not be greater than 100 characters
    <expiryDays> must be between <1> and <365>

    Return values:
    successfully pasted (<dict>):
        {
            "type": "success",
            "data": <str>; the URL of the paste
        }
    <title> has more than 100 characters (<dict>):
        {
            "type": "failure",
            "data": <str>; the reason for failure
        }
    """
    paste = {"content": content,
             "syntax": syntax,
             "title": title,
             "poster": poster,
             "expiry_days": expiryDays}
    data = requests.post("http://dpaste.com/api/v2/", data = paste).text
    if data[:len("http://")] == "http://":
        return {"type": "success", "data": data}
    return {"type": "failure", "data": data}
