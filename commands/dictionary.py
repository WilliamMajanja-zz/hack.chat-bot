#!/usr/bin/env python3

import requests
import json


def definitions(appId, appKey, word, lang = "en"):
    """Returns a definition (string) or <None> if a definition was or wasn't found respectively.

    Keyword arguments:
    appId -- string; Oxford Dictionaries API ID
    appKey -- string; Oxford Dictionaries API Key
    word -- the word to be defined
    lang -- optional string; the language to use (e.g., <"en"> for English)
    """

    url = "https://od-api.oxforddictionaries.com/api/v1/entries/{}/{}".format(lang, word.lower())
    site = requests.get(url, headers = {"app_id": appId, "app_key": appKey})
    if not site:
        return
    data = site.json()
    return data["results"][0]["lexicalEntries"][0]["entries"][0]["senses"][0]["definitions"][0]
