#!/usr/bin/env python3

import requests
import json


def yo_momma():
    """Returns a random yo momma joke (<str>)."""
    data = requests.get("http://api.yomomma.info/").text
    return json.loads(data)["joke"]
