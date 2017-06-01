#!/usr/bin/env python3

import requests
import json


def yo_momma():
    """Returns a random yo momma joke (str)."""
    return json.loads(requests.get("http://api.yomomma.info/").text)["joke"]
