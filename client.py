import socket
import threading
import sys
from operator import truediv

reset_input_thing = False

def usage():
    print("IRC simple Python client\n")
    print("$ ./irc_client.py USERNAME CHANNEL\n")
    print("where: USERNAME - your username, CHANNEL - channel you'd like to join (eg. channelname or #channelname)")


def channel(channel):
    if channel.startswith("#") == False:
        return "#" + channel
    return channel

# helper function used as thread target
def print_response():
    global reset_input_thing
    resp = client.get_response()
    if resp:
        msg = resp.strip().split(":")
        print("\n")
        print("< {}> {}".format(msg[1].split("!")[0], msg[2].strip()))
        reset_input_thing = True

class IRCSimpleClient:

    def __init__(self, username, channel, server="irc.freenode.net", port=6667):
        self.username = username
        self.server = server
        self.port = port
        self.channel = channel

    def connect(self):
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect((self.server, self.port))

    def get_response(self):
        return self.conn.recv(512).decode("utf-8")

    def send_cmd(self, cmd, message):
        command = "{} {}\r\n".format(cmd, message).encode("utf-8")
        self.conn.send(command)

    def send_message_to_channel(self, message):
        command = "PRIVMSG {}".format(self.channel)
        message = ":" + message
        self.send_cmd(command, message)

    def join_channel(self):
        cmd = "JOIN"
        channel = self.channel
        self.send_cmd(cmd, channel)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        usage()
        exit(0)
    else:
        username = sys.argv[1]
        channel = channel(sys.argv[2])

    cmd = ""
    joined = False
    client = IRCSimpleClient(username, channel)
    client.connect()

    while(joined == False):
        resp = client.get_response()
        print(resp.strip())
        if "No Ident response" in resp or "Found your hostname" in resp or "Could not resolve" in resp:
            client.send_cmd("NICK", username)
            client.send_cmd(
                "USER", "{} * * :{}".format(username, username))

        # we're accepted, now let's join the channel!
        if "376" in resp:
            client.join_channel()

        # username already in use? try to use username with _
        if "433" in resp:
            username = "_" + username
            client.send_cmd("NICK", username)
            client.send_cmd(
                "USER", "{} * * :{}".format(username, username))

        # if PING send PONG with name of the server
        if "PING" in resp:
            client.send_cmd("PONG", ":" + resp.split(":")[1])

        # we've joined
        if "366" in resp:
            joined = True

    while(cmd != "/quit"):
        cmd = input("< {}> ".format(username)).strip()
        if reset_input_thing:
            print("\n< {}> ".format(username))
            reset_input_thing = False
        if cmd == "/quit":
            client.send_cmd("QUIT", "Good bye!")
        client.send_message_to_channel(cmd)


        threading.Thread(target=print_response).start()