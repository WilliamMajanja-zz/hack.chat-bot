# hack.chat bot

This is a bot running on [hack.chat](https://hack.chat/) for general usage. It is meant to perform tasks quicker than they would have
without it. 

You can check it out by going to [?programming](https://hack.chat/?programming) and entering `.help` to get a list of commands.
It may or may not be there under the name `neelkamath_bot` as I do not have the resources to run it on a server and hence it only runs
when my computer is on.

# Installation

## Prerequisites

- [Python 3 or higher](https://www.python.org/downloads/)
- hackchat: API wrapper to connect to the website `pip install hackchat`
- BeautifulSoup 4: library to screen scrape `pip install bs4`
- requests: HTTP library `pip install requests`

## Building the code

1. Clone the repository: `git clone https://github.com/neelkamath/hack.chat-bot`
1. Create a file named `settings.py` in the root directory and paste the following code into it.
    ```python
    #!/usr/bin/env python3


    name = ""
    tripcode = ""
    channel = ""
    ```
    1. Enter the name of the bot in `name` (e.g., "myBot").
    1. Optionally, enter the bots [tripcode](https://en.wikipedia.org/wiki/Imageboard#Tripcodes) in `tripcode` (e.g., "password123").
    1. Enter the channel to connect to in `channel` (e.g., "programming").
    
# Usage

1. Change the directory: `cd hack.chat-bot`
1. Run the script.
    - Windows: `python bot.py`
    - Linux: `python3 bot.py`

![Commands](screenshot.png)

# License

This project is under the [MIT License](LICENSE.txt).
