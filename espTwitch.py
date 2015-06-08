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

class IRCClient(pytwitcherapi.IRCClient):

    def __init__(self, *args, **kwargs):
        super(IRCClient, self).__init__(*args, **kwargs)
        self.current_direction = FORWARD

    def on_pubmsg(self, connection, event):
        super(IRCClient, self).on_pubmsg(connection, event)
        message = self.messages.get()
        print ('{0}: {1}'.format(message.source.nickname, message.text))
        self.process(message.text)

    def on_privmsg(self, connection, event):
        super(IRCClient, self).on_pubmsg(connection, event)
        message = self.messages.get()
        print ('{0}: {1}'.format(message.source.nickname, message.text))
        self.process(message.text)

    def process(self, text):
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
    session.start_login_server()
    url = session.get_auth_url()
    webbrowser.open(url)
    input("Please authorize Pytwitcher in the browser then press ENTER!")
    assert session.authorized, "Authorization failed! Did the user allow it?"


def create_client(session):
    channel = session.get_channel('mgolub2')
    return IRCClient(session, channel)

@app.route('/')
def hello_world():
    return 'Hello World!'

#@app.route('')

@app.route('/move')
def move():
    try:
        return str(direction_queue.get_nowait())
    except queue.Empty:
        return str(COAST)
    except Exception as e:
        print(e)

if __name__ == '__main__':
    session = pytwitcherapi.TwitchSession()
    authorize(session)
    client = create_client(session)
    t = threading.Thread(target=client.process_forever)
    t.start()
    #while True:
    #    time.sleep(10)
    app.run(host='0.0.0.0', port=8000)
