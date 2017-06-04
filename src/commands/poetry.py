#!/usr/bin/env python3

import requests
import json


def poems(search, isAuthor):
    """Returns poems with their titles and authors.

    Keyword arguments:
    search -- <str>; the name of the poem or poet
    isAuthor -- <bool>; set to <True> if <search> is the name of a poet
                or <False> if <search> is the name of a poem

    Return values:
    poem(s) found (<list>):
        [
            {
                "title": <str>; title of poem,
                "author": <str>; author of poem,
                "poem": <str>; the poem
            },
        ]
    no poem found (<None>):
        <None>
    """
    which = "author" if isAuthor else "title"
    url = "http://poetrydb.org/{}/{}".format(which, search)
    data = requests.get(url).text
    data = json.loads(data)
    if "status" in data:  # A status is sent only if the search failed.
        return None
    data = data[0]
    poems = []
    for part in data:
        poem = {"title": data["title"], "author": data["author"],
                "poem": "\n".join(data["lines"])}
        poems.append(poem)
    return poems
