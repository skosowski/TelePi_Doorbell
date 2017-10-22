# TelePi Doorbell

The goal of this project is to create an internet-connected doorbell which will do the following:

* notify user(s) on a mobile device when someone uses the doorbell
* take a picture of the caller
* play audio message to the caller, e.g. I'm not at home, please call me at XXX

There are devices on the market that can do that and lot more, but why not use your spare raspberry pi for that?

To make it simple and reliable, we'll use the following:

 * [Telegram bot for messanging](https://core.telegram.org/bots) and [Python Telepot API](https://github.com/nickoala/telepot)
 * [Amazon Polly](https://aws.amazon.com/polly/) to generate audio messages (you can do it on-the-fly using API, but I'm lazy and used the console to generate one-time mp3). There's a free-tier for Polly.
 * Raspberry pi camera
 * [Healthchecks](https://healthchecks.io/) to monitor your device

### How-to:

I'm skipping the obvious parts, which are broadly documented on the net (e.g. installing pip3 or setting up ordinary Telegram Bot). I'm using Python 3.5. 

1. Enable camera in Raspberry pi Configurtion
2. Install python3 and pip3. Using pip3 install all packages like requests, telepot, etc.
3. Set-up your Telegram bot using Telegram Botfather; generate API key and put it in telebot.ini file. 
4. Set-up a group (or supergroup as in my case). Write a message to your bot from group or your user. Check your chat_id using following:
 ``` 
 content_type, chat_type, chat_id = telepot.glance(msg)
 print(content_type, chat_type, chat_id, sep=" ")
 ```
5. I wanted to limit access to my bot via chat_id, so it replies only to a specified person/group (configured in telebot.ini)
6. Register on healthchecks.io and get your unique link. Place it in telebot.ini file
7. Optionally enable ssh and change default password/enable key auth
8. I set up an ugly cronjob as default user to run at startup:

```
@reboot sleep 60 && /usr/bin/python3 /dir/to/your/script/telebot.py /dir/to/your/script/
```
9. I've set up GPIO input on pin 4; when ringing the bell, it closes circuit between pin 4 and GND. I have 5k Ohm resistor in between (circuit is Pin 4 - Button - Resistor - GND). Obviously you can use a different pin, resistance value, use 3.3V value instead of GND edge triggering, etc.
10. There is configurable debouncing for keypresses. I assume that minimum pause between doorbell keypresses is 2 seconds. You can configure that in telebot.ini file.

### Further work:
Obviously, the most desirable feature would be to have bi-directional call, I'm figuring out if there is a simple enough method to do it using Telegram bot. 

Other than that, I plan to add temperature measurement. 

### Other notes:
Remember, you're using open Telegram infrastructure and hence storing your data there. As a sanity check, I use supergroup, which allows deleting all messages from the bot for all users (like clean history for all). Use common sense (e.g. I don't plan to enable door opening using this bot). 

