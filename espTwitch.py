"""
Super simple way to send commands to an esp8266 that is polling /move
for commands. These commands are sent to a motorized tank running FreeRTOS,
which will interpret the integers as movement commands
Most of the twich code is from the pytwitchapi examples chatcli.py file,
from here: https://raw.githubusercontent.com/Pytwitcher/pytwitcherapi/master/examples/chatcli.py
"""
from flask import Flask
import threading
import webbrowser
import pytwitcherapi
import queue
import time

app = Flask(__name__)
LEFT = 4
RIGHT = 8
FORWARD = 2
BACKWARD = 1
COAST = 0
direction_queue = queue.Queue()

last_direction = COAST

class IRCClient(pytwitcherapi.IRCClient):
    """
    Send both public and private messages from the twitch irc 
    stream to a mehtod that will look for valids directives,
    then place the resulting direction number into the direction_queue
    """


    def on_pubmsg(self, connection, event):
        """
        Grab messages, and send them off for processing
        """
        super(IRCClient, self).on_pubmsg(connection, event)
        message = self.messages.get()
        print ('{0}: {1}'.format(message.source.nickname, message.text))
        self.process(message.text)

    def on_privmsg(self, connection, event):
        """
        Redirect private messages to be process by the public message handler
        """
        self.on_pubmsg(self, connection, event)

    def process(self, text):
        """
        Looks at the first character of a message for a match with 
        f, b, r, or l to set the correpsonding direction, then 
        send that off into the queue. 
        """
        if text[0].lower() == 'f':
            self.current_direction = FORWARD
        elif text[0].lower() == 'b':
            self.current_direction = BACKWARD
        elif text[0].lower() == 'r':
            self.current_direction = RIGHT
        elif text[0].lower() == 'l':
            self.current_direction = LEFT
        direction_queue.put_nowait(self.current_direction)

def authorize(session):
    """
    Authorize with the twitch api, so we can attach the the chat stream
    """
    session.start_login_server()
    url = session.get_auth_url()
    webbrowser.open(url)
    input("Please authorize Pytwitcher in the browser then press ENTER!")
    assert session.authorized, "Authorization failed! Did the user allow it?"


def create_client(session):
    """
    Attach a session to a channel for the IRC client to listen too.
    """
    channel = session.get_channel('mgolub2')
    return IRCClient(session, channel)

@app.route('/')
def hello_world():
    """
    For that cheery optimism
    """
    return 'Hello World!'


@app.route('/move')
def move():
    """
    Grab the top of the directio_queue and return it. The esp8266
    will call this method every so often to get the next movement 
    direction
    """
    try:
        last_direction = direction_queue.get_nowait()
        return "~"+str(last_direction)+"~"
    except queue.Empty:
        return "~"+str(last_direction)+"~"
    except Exception as e:
        print(e)

if __name__ == '__main__':
    #Setup the twitch api, and start a seperate thread for the irc client
    session = pytwitcherapi.TwitchSession()
    authorize(session)
    client = create_client(session)
    t = threading.Thread(target=client.process_forever)
    t.start()
    app.run(host='0.0.0.0', port=8000)
