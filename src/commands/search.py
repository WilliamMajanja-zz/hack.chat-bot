#!/usr/bin/env python3

import requests
import json


def duckduckgo(search, appName=""):
    """Gives instant answers from DuckDuckGo (https://duckduckgo.com/).

    Keyword arguments:
    search -- <str>; what you are searching for (case sensitive)
    appName -- <str>; the name of your app

    Return value:
    {
        "AbstractText": <str>; topic summary,
        "AbstractSource": <str>; name of <AbstractText> source,
        "Heading": <str>; name of topic that goes with <AbstractText>,
        "Answer": <str>; instant answer,
        "Definition": <str>; dictionary definition (may differ from
                      <AbstractText>),
        "DefinitionSource": <str>; name of <Definition> source,
        "DefinitionURL": <str>; deep link to expanded definition page in
                         <DefinitionSource>
        "URL": <str>; URL associated with <AbstractText>,
        "URLText": <str>; text from <FirstURL>
    }
    """
    url = "http://api.duckduckgo.com/?q={}&format=json&t={}"
    url = url.format(search, appName)
    data = requests.get(url).text
    data = json.loads(data)
    items = {"AbstractText": data["AbstractText"],
             "AbstractSource": data["AbstractSource"],
             "Heading": data["Heading"],
             "Answer": data["Answer"],
             "Definition": data["Definition"],
             "DefinitionSource": data["DefinitionSource"],
             "DefinitionURL": data["DefinitionURL"]}
    exists = True if len(data["Results"]) > 0 else False
    items["URL"] = data["Results"][0]["FirstURL"] if exists else ""
    items["URLText"] = data["Results"][0]["Text"] if exists else ""
    return items
