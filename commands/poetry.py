#!/usr/bin/env python3

import requests
import json


def poems(search, isAuthor):
    """Returns poems with their titles and authors.

    Keyword arguments:
    search -- string; the name of the author or poem
    isAuthor -- bool; set to <True> if <search> is the name of a poet or <False> if <search> is the name of a poem

    Return values:
    poetry -- list; a list containing dictionaries of the form {"title": title, "author": author, "poem": poem}
    None -- None; if no poems were found
    """

    url = "http://poetrydb.org/{}/{}".format("author" if isAuthor else "title", search)
    data = json.loads(requests.get(url).text)
    if "status" in data: # http://poetrydb.org sends a status only if the search failed.
        return
    parts = []
    for part in data:
        parts.append(part)
    poems = []
    for part in parts:
        poems.append({"title": part["title"], "author": part["author"], "poem": "\n".join(part["lines"])})
    return poems
