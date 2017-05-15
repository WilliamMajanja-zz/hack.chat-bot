#!/usr/bin/env python3

"""Contains functionality from various dictionaries."""

import requests
import json


class OxfordDictionary():
    """Uses the Oxford Dictionaries API for language tools such as definitions and translations.

    Keyword arguments:
    appId -- string; Oxford Dictionaries API ID
    appKey -- string; Oxford Dictionaries API Key
    """

    def __init__(self, appId, appKey):
        """Authorizes the application."""
        self.appId = appId
        self.appKey = appKey

    def define(self, word, lang = "en"):
        """Returns a definition..

        Keyword arguments:
        word -- the word to be defined
        lang -- optional string; an IANA language code indicating which language to use (e.g., <"en"> for English)

        Return values:
        definition -- string; the definition for <word>
        404 -- int; the status code if the word wasn't found
        500 -- int; the status code if there was a processing error
        None -- <None>; if the word was found but there wasn't a definition
        """

        url = "https://od-api.oxforddictionaries.com/api/v1/entries/{}/{}".format(lang, word.lower())
        site = requests.get(url, headers = {"app_id": self.appId, "app_key": self.appKey})
        if site.status_code == 404 or site.status_code == 500: # 404: NOT FOUND; 500: PROCESSING ERROR
            return site.status_code
        data = site.json()
        data = data["results"][0]["lexicalEntries"][0]["entries"][0]["senses"][0]
        if "definitions" in data:
            return data["definitions"][0]

    def translate(self, word, srcLang, targetLang):
        """Returns a translation of <word> or <None> if no translations were found.

        Keyword arguments:
        word -- string; the word to be translated
        srcLang -- string; the IANA language code indicating which language <word> is in
        targetLang -- string; the IANA language code indicating which language <word> should be translated to

        Return values:
        translation -- string; the translation of <word>
        400 -- int; the status code if <targetLang> isn't known
        404 -- int; the status code if no translation was found
        500 -- int; the status code if there was a processing error
        None -- <None>; if the word was found but a translation doesn't exist

        The languages supported are (IANA language code: language name)
        en: English
        es: Spanish, Castilian
        nso: Pedi, Northern Sotho, Sepedi
        ro: Romanian, Moldavian, Moldovan
        ms: Malay
        zu: Zulu
        id: Indonesian
        tn: Tswana
        """

        url = "https://od-api.oxforddictionaries.com:443/api/v1/entries/{}/{}/translations={}"
        url = url.format(srcLang, word.lower(), targetLang)
        site = requests.get(url, headers = {"app_id": self.appId, "app_key": self.appKey})
        # STATUS CODES:
        # 400: <targetLang> IS UNKNOWN
        # 404: NO TRANSLATION FOUND
        # 500: INTERNAL ERROR
        if site.status_code == 400 or site.status_code == 404 or site.status_code == 500:
            return site.status_code
        data = site.json()
        data = data["results"][0]["lexicalEntries"][0]["entries"][0]["senses"][0]
        try:
            if "subsenses" in data:
                return data["subsenses"][0]["translations"][0]["text"]
            return data["translations"][0]["text"]
        except KeyError:
            return


def urban_dictionary(search):
    """Returns a definition from Urban Dictionary using <search>.

    Return values:
    data -- dict; {"word": word, "definition": definition, "permalink": permalink} if there's a definition for <search>
    None -- None; if no definition was found with <search>
    """

    url = "http://api.urbandictionary.com/v0/define?term={}".format(search)
    data = json.loads(requests.get(url).text)
    if data["result_type"] == "no_results":
        return
    data = data["list"][0]
    return {"word": data["word"], "definition": data["definition"], "permalink": data["permalink"]}
