#!/usr/bin/env python3

import bs4
import requests


def quotes(person):
    """This returns a list of quotes from <person>."""
    query = person.replace(" ", "+")
    soup = bs4.BeautifulSoup(requests.get("https://brainyquote.com/search_results.html?q=" + query).text, "html.parser")
    quotes = []
    for link in soup.find_all("a"):
        if "quotes/quotes" in str(link):
            if link.text:
                quotes.append(str(link.text))
    return quotes
