# instagram-bot
A simple yet powerful Instagram Bot, which uses the newly introduced web direct messages to provide some utility on the go.
The interface language is mostly german.

## 1. Features:
- A list of useful commands
- download public / visible Posts by sending them via dm
- *Will code it eventually (or not)*: !stats: See in depth stats of a public account (WIP: `instascraper.py`)
- *Will code it eventually (or not)*: Leave some nice comments from the vocabulary list under Posts of user in the spam list

## 2. Public Commands:
- **!help, !h, !hilfe:** shows a command list and description
- **!wiki, !w \<Word\>:** get information on a topic quickly from wikipedia
- **!calc, !math, !m \<Term\>:** a little calculator on the go, that can compute a whole term with brackets (), roots r(), powers ()^() and even some trigonometrial functions sin(), cos(), tan()
- **!translate, !trans, !t \<Language\> \<Text\> or just \<Text\>:** use google translate to translate within: fr (french), de (german), en (english), kr (korean), ja (japanese), fi (finnish), la (latin)
- **!lyrics, !l \<Word\>:** Get a songtext quickly from Genius
- **!anime, !a \<Anime\>:** Well, you guessed it - get the synopsis of an Anime from MyAnimeList
- **!vorschlag, !v: \<Text\>** send feedback and improvements, will be saved in a specific log file

## 3. Moderator Commands:
these are mostly unfinished (see `instascraper.py`), cause i'm not sure if its a good idea to have my bot spam people.
- **!list:** Shows the list of spammed users
- **!adduser, !add <@Name> / !deluser, !del <@Name>:** adds and deletes user to/from this list
- **!addtext, !addt \<Text\> / !deltext, !delt \<Text\>:** adds and deletes vocabulary, which the bot uses to spam

## 4. Admin Commands:
these commands can only be used by the people marked as admins in the config.py.
- **!addmod, !addm \<Name\> / !delmod, !delm \<Name\>:** add and remove Moderators from the Mod List.

## 5. Installation:
Instructions and Requirements to run your own bot:
- Python 3 + Pip packages wikipedia googletrans emoji requests lyricsgenius
- Selenium, a Selenium compatible browser (FF or Chrome) and geckodriver(.exe) or chromedriver(.exe) in the `driver/` folder
- Set up the config.py
