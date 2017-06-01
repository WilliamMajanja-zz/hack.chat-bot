#!/usr/bin/env python3

import requests


def convert(apiKey, fromCode, toCode):
    """Gives how much <toCode> is equal to 1 <fromCode> (currency conversion rate).

    Keyword arguments:
    apiKey -- str; the https://www.exchangerate-api.com/ api key
    fromCode -- str; the code from ISO 4217 Three Letter Currency Codes to use as the base conversion
    toCode -- str; the code from ISO 4217 Three Letter Currency Codes to convert <fromCode> to

    Return values:
    rate -- float; conversion rate of <fromCode> to <toCode>
    unknown-code -- str; currency code unsupported by https://www.exchangerate-api.com/
    invalid-key -- str; <apiKey> is either inactive or doesn't exist
    quota-reached -- str; the supplied <apiKey> has exhausted its quota
    """
    url = "https://v3.exchangerate-api.com/pair/{}/{}/{}".format(apiKey, fromCode, toCode)
    data = requests.get(url).json()
    if data["result"] != "success":
        return data["error"]
    return data["rate"]
