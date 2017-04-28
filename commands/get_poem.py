#!/usr/bin/env python3

import re
import random
import datetime

import bs4
import requests


def get_poem(name, poet = False):
    """Returns a tuple with its first element as a poem and its second element as a link to its webpage.
    Keyword arguments:
    name -- the poem's or poet's name (either in part or in full)
    poet -- set to <True> if <name> is the name of a poet or <False> if <name> is the name of a poem
    <None> will be returned if no poem was found.
    """

    random.seed(datetime.datetime.now())
    url = "https://www.poemhunter.com/"
    query = " ".join(name.split())
    query = query.replace(" ", "+").lower()
    soup = bs4.BeautifulSoup(requests.get(url + "search/?q=" + query).text, "html.parser")
    if poet:
        found = False
        for link in soup.find_all("a"):
            address = str(link.get("href"))
            data = re.sub("/", "", address)
            data = re.sub("-", " ", data)
            if name in data and re.search(r"\s", data):
                soup = bs4.BeautifulSoup(requests.get(url + address + "poems/").text, "html.parser")
                found = True
                break
        if not found:
            return
        poems = []
        for link in soup.find_all("a"):
            if re.match("/poem/", str(link.get("href"))):
                poems.append(url + str(link.get("href")))
        while True:
            if not len(poems):
                return
            page = poems[random.randint(0, len(poems) - 1)]
            soup = bs4.BeautifulSoup(requests.get(page).text, "html.parser")
            try:
                body = str(soup.find_all("body"))
            except RecursionError:
                poems.remove(page)
                continue
            break
    else:
        poem = False
        for link in soup.find_all("a"):
            if re.match("/poem/", str(link.get("href"))):
                page = url + str(link.get("href"))
                soup = bs4.BeautifulSoup(requests.get(page).text, "html.parser")
                poem = True
                try:
                    body = str(soup.find_all("body"))
                except RecursionError:
                    poem = False
                    continue
                break
        if not poem:
            return
    while True:
        poemStart = re.search("<p>", body)
        poemEnd = re.search("</p>", body)
        poem = body[poemStart.end():poemEnd.start()]
        if "\n" in poem:
            poem = " ".join(poem.split())
            poem = re.sub(r"<br(/)*>(\s)*", "\n", poem)
            poem = str(soup.h1.text) + "\n\n" + poem.strip()
            return (poem, page)
        body = body[poemEnd.end():]
