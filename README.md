# About

You can check out this general use bot by going to [hack.chat/?programming](?programming).

# Building the code

## Prerequisites

- [Python 3 or higher](https://www.python.org/downloads/)
- hackchat `pip install hackchat`
- BeautifulSoup 4 `pip install bs4`
- requests `pip install requests`

## Building

1. Clone the repository `git clone https://github.com/neelkamath/hack.chat-bot`
1. Create a file named `settings.py` in the root directory and paste the following code into it.
    ```python
    #!/usr/bin/env python3


    name = ""
    tripcode = ""
    channel = ""
    ```
    Enter the name of the bot in <name> (e.g. "myBot").
    Optionally, enter the bots [tripcode](https://en.wikipedia.org/wiki/Imageboard#Tripcodes) in <tripcode> (e.g. "py").
    Enter the channel to connect to in <channel> (e.g. "coding").
1. Change the directory `cd hack.chat-bot`
1. Run the script by entering one of the following on the command line.
    - Windows: `python bot.py`
    - Linux: `python3 bot.py`
