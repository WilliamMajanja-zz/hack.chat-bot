#!/usr/bin/env python3

import requests
import json


class Dictionary():
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
        """Returns a definition (string) or <None> if a definition was or wasn't found respectively.

        Keyword arguments:
        word -- the word to be defined
        lang -- optional string; an IANA language code indicating which language to use (e.g., <"en"> for English)
        """

        url = "https://od-api.oxforddictionaries.com/api/v1/entries/{}/{}".format(lang, word.lower())
        site = requests.get(url, headers = {"app_id": self.appId, "app_key": self.appKey})
        if site.status_code == 404 or site.status_code == 500: # 404: NO DEFINITION, 500: PROCESSING ERROR
            return
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
            return
        data = site.json()
        data = data["results"][0]["lexicalEntries"][0]["entries"][0]["senses"][0]
        try:
            if "subsenses" in data:
                return data["subsenses"][0]["translations"][0]["text"]
            return data["translations"][0]["text"]
        except KeyError:
            return
