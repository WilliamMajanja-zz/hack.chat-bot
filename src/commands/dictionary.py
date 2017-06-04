#!/usr/bin/env python3

"""Contains functionality from various dictionaries."""

import re
import requests
import json


class Oxford():
    """Uses the Oxford Dictionaries API for tools like translations.

    You can get API keys at https://developer.oxforddictionaries.com/.
    """

    def __init__(self, appId, appKey):
        """Gets credentials.

        Keyword arguments:
        appId -- <str>; Oxford Dictionaries API ID
        appKey -- <str>; Oxford Dictionaries API Key
        """
        self.appId = appId
        self.appKey = appKey

    def define(self, word, lang="en"):
        """Returns a definition.

        Keyword arguments:
        word -- <str>; the word to be defined
        lang -- <str>; the IANA language code for the definition

        Return values:
        definition found (<dict>):
            {
                "type": "success",
                "response": <str>; the definition of <word>
            }
        <word> not found (<dict>):
            {
                "type": "failure",
                "response": 400
            }
        <word> found sans definition (<dict>):
            {
                "type": "failure",
                "response": None
            }
        processing error (<dict>):
            {
                "type": "failure",
                "response": 500
            }
        """
        url = "https://od-api.oxforddictionaries.com/api/v1/entries/{}/{}"
        url = url.format(lang, word.lower())
        headers = {"app_id": self.appId, "app_key": self.appKey}
        site = requests.get(url, headers = headers)
        if site.status_code == 404 or site.status_code == 500:
            return {"type": "failure", "response": site.status_code}
        data = site.json()
        data = data["results"][0]["lexicalEntries"][0]["entries"][0]
        data = data["senses"][0]
        if "definitions" in data:
            return {"type": "success", "response": data["definitions"][0]}
        else:
            return {"type": "failure", "response": None}

    def translate(self, word, targetLang, srcLang="en"):
        """Translates <word> from <srcLang> to <targetLang>.

        Keyword arguments:
        word -- <str>; the word to be translated
        srcLang -- <str>; the IANA language code <word> is in
        targetLang -- <str>; the IANA language code to translate to

        The following IANA language codes are accepted.
        "en" for English
        "es" for Spanish, Castilian
        "nso" for Pedi, Northern Sotho, Sepedi
        "ro" for Romanian, Moldavian, Moldovan
        "ms" for Malay
        "zu" for Zulu
        "id" for Indonesian
        "tn" for Tswana

        Return values:
        <word> was successfully translated (<dict>):
            {
                "type": "success",
                "response": <str>; the translation of <word>
            }
        <targetLang> is unknown (<dict>):
            {
                "type": "failure",
                "response": 400
            }
        no translation found (<dict>):
            {
                "type": "failure",
                "response": 404
            }
        processing error (<dict>):
            {
                "type": "failure",
                "response": 500
            }
        <word> was found but no translation was found (<dict>):
            {
                "type": "failure",
                "response": None
            }
        """
        url = ("https://od-api.oxforddictionaries.com:443/api/v1/entries/"
               + "{}/{}/translations={}")
        url = url.format(srcLang, word.lower(), targetLang)
        headers = {"app_id": self.appId, "app_key": self.appKey}
        site = requests.get(url, headers = headers)
        if re.match(r"400|404|500", str(site.status_code)):
            return {"type": "failure", "response": site.status_code}
        data = site.json()
        data = data["results"][0]["lexicalEntries"][0]["entries"][0]
        data = data["senses"][0]
        if "subsenses" in data:
            data = data["subsenses"][0]["translations"][0]["text"]
        elif "translations" in data:
            data = data["translations"][0]["text"]
        else:
            return {"type": "failure", "response": None}
        return {"type": "success", "response": data}


def urban(search):
    """Gives definitions from Urban Dictionary.

    Urban Dictionary is a crowdsourced online dictionary of slang words
    and phrases (http://www.urbandictionary.com/).

    Keyword arguments:
    search -- <str>; the term to be searched for

    Return values:
    a definition for <search> was found (<dict>):
        {
            "word": <str>; the word being defined,
            "definition": <str>; the definition of <word>,
            "permalink": <str>; permalink to definition
        }
    no definition found:
        <None>
    """
    url = "http://api.urbandictionary.com/v0/define?term={}".format(search)
    data = requests.get(url).text
    data = json.loads(data)
    if data["result_type"] == "no_results":
        return None
    data = data["list"][0]
    return {"word": data["word"], "definition": data["definition"],
            "permalink": data["permalink"]}
