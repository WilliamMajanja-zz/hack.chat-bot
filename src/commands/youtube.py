#!/usr/bin/env python3

import bs4
import requests


def videos(search):
    """Returns a dictionary of YouTube videos found with <search> of the form <{name: link}>."""
    youtube = "https://www.youtube.com/"
    results = "results?search_query="
    query = search.replace(" ", "+")
    soup = bs4.BeautifulSoup(requests.get(youtube + results + query).text, "html.parser")
    vids = {}
    for link in soup.find_all("a"):
        title = str(link.get("title"))
        href = str(link.get("href"))
        if title != "None" and "/watch" in href:
            vids[title] = youtube + href
    return vids
