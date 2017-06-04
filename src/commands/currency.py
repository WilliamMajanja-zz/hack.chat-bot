#!/usr/bin/env python3

import requests


def convert(apiKey, fromCode, toCode):
    """Gives the currency conversion from <fromCode> to <toCode>.

    Get the API key from https://www.exchangerate-api.com/.
    Currency codes must be from ISO 4217 Three Letter Currency Codes.

    Keyword arguments:
    apiKey -- <str>; the API key
    fromCode -- <str>; the currency code for the base conversion
    toCode -- <str>; the currency code to convert to

    Return values:
    successful conversion (<dict>):
        {
            "type": "success",
            "response": <float>; the conversion rate
        }
    unsupported currency code (<dict>):
        {
            "type": "failure",
            "response": "unknown-code"
        }
    <apiKey> is either inactive or doesn't exist (<dict>):
        {
            "type": "failure",
            "response": "invalid-key"
        }
    <apiKey> has exhausted its quota (<dict>):
        {
            "type": "failure",
            "response": "quota-reached"
        }
    """
    url = "https://v3.exchangerate-api.com/pair/{}/{}/{}"
    url = url.format(apiKey, fromCode, toCode)
    response = requests.get(url).json()
    if response["result"] != "success":
        return {"type": "failure", "response": response["error"]}
    return {"type": "success", "response": response["rate"]}
