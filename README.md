# hack.chat bot

This is a bot running on [hack.chat](https://hack.chat/) for general usage. It is meant to perform tasks quicker than
they would have without it.

# Using the bot

If the bot, `neelkamath_bot`, is online, you can check it out by entering `.help` on ?programming.

# Local install for developers

## Prerequisites

- [Python 3 or higher](https://www.python.org/downloads/)
- Install the dependencies: `pip install -r requirements.txt`
- [Oxford Dictionaries API tokens](https://developer.oxforddictionaries.com/documentation/getting_started)

## Building

1. Clone the repository: `git clone https://github.com/neelkamath/hack.chat-bot`

# Usage

1. Change the directory: `cd hack.chat-bot`
1. Run the script.
    - Windows: `python bot.py`
    - Linux: `python3 bot.py`

![Commands](screenshot.png)

# Contributing

Make sure your code is [PEP 8](https://www.python.org/dev/peps/pep-0008/) compliant with the exception that line lengths
are to be limited to 120 characters instead of 79. Make sure you aren't adding an existing feature. Here are some
features that would be nice to have:

- conversational AI
- jokes
- afk
    - The user tells the bot that they are afk.
    - The bot tells people @-mentioning the afk user that they are afk.
    - The afk status is removed upon receiving the users next message.
- calculator
- give the output of python code
- google search
- leave a message
    - The user tells the bot to message a person.
    - The bot will send the message to the person the next time they join or send a message.
- urban dictionary definitions
- Tell what the time is in another place.
- The bot will tell what the user usually names themselves upon being given a trip code.
- currency converter
- use an API to get poems instead of screen scraping
- use an API to get quotes from famous people instead of screen scraping
- use an API to search YouTube instead of screen scraping

# License

This project is under the [MIT License](LICENSE.txt).
