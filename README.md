#Twitch to esp8266 (Or whatever can make a GET request...)

A super basic super simple server to gather direction commands from a twitch
chat and send those of to an esp8266 perodically getting from /move.
The esp8266 controls a cool tank running FreeRTOS, for EE 472 at the 
Univeristy of Washington

##Requires:
* pytwitcherapi
* Flask
Tested on Python 3, should work on Python 2.
