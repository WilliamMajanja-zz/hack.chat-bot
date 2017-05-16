#!/usr/bin/env python3

import requests
import json


def duckduckgo(search, appName = ""):
    """Returns instant answers from DuckDuckGo (https://duckduckgo.com/).

    Keyword arguments:
    search -- string; what you are searching for (case sensitive)
    appName -- string; the name of the app you are using to access DuckDuckGo's API

    Return values:
    data -- dictionary of the form {"AbstractText": topic summary,
                                    "AbstractSource": name of <AbstractText> source,
                                    "Heading": name of topic that goes with <AbstractText>,
                                    "Answer": instant answer,
                                    "Definition": dictionary definition (may differ from <AbstractText>),
                                    "DefinitionSource": name of <Definition> source,
                                    "DefinitionURL": deep link to expanded definition page in <DefinitionSource>
                                    "URL": URL associated with <AbstractText>,
                                    "URLText": text from <FirstURL>}
            Only items containing data will be returned.
    """

    data = requests.get("http://api.duckduckgo.com/?q={}&format=json&t={}".format(search, appName))
    data = json.loads(data.text)
    items = {"AbstractText": data["AbstractText"],
             "AbstractSource": data["AbstractSource"],
             "Heading": data["Heading"],
             "Answer": data["Answer"],
             "Definition": data["Definition"],
             "DefinitionSource": data["DefinitionSource"],
             "DefinitionURL": data["DefinitionURL"]}
    info = {}
    for item in items:
        if len(items[item]) > 0:
            info[item] = items[item]
    if len(data["Results"]) > 0:
        info["URL"] = data["Results"][0]["FirstURL"]
        info["URLText"] = data["Results"][0]["Text"]
    return info
