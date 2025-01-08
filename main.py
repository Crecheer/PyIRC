import socket
import sys
import threading
import encodings

def channel(channel):
    if channel.startswith("#") == False:
        return "#" + channel
    else:
        return channel
    
# Thread helper function
def print_response():
    while cmd != "/quit":
        resp = client.get_response()

        if resp:
            msg = resp.strip().split(":")
            print(resp)
            print("< {}> {}".format(msg[1].split("!")[0], msg[2].strip()))

class IRCClient:

    def __init__(self, username, channel, server="irc.freenode.net", port=6667):
        self.username = username
        self.channel = channel
        self.server = server
        self.port = port


    def connect(self):
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect((self.server, self.port))

    def get_response(self):
        return self.conn.recv(512).decode("utf-8")

    def send_cmd(self, cmd, message):
        command = "{} {}\r\n".format(cmd, message).encode("utf-8")
        self.conn.send(command)
        print("sent cmd: {}".format(command.decode("utf-8")))
    
    def send_message(self, message):
        command = "PRIVMSG {}".format(self.channel)
        message = ":" + message
        self.send_cmd(command, message)

    def join_channel(self):
        command = "JOIN"
        channel = self.channel
        self.send_cmd(command, channel)

if __name__ == "__main__":
    if sys.argv[1] == "help":
        print("usage: ./irc_client.py USERNAME CHANNEL\nwhere: USERNAME - your username, CHANNEL - channel you'd like to join (eg. channelname or #channelname)")
        quit()
    username = sys.argv[1]
    channel = channel(sys.argv[2])
    cmd = ""
    joined = False
    client = IRCClient(username, channel)
    client.connect()

    while(joined == False):
        resp = str(client.get_response())
        print(resp.strip())

        if "Could not resolve your hostname" in resp.strip():
            client.send_cmd("NICK", username)
            client.send_cmd("USER", "{} * * :{} ".format(username, username))

        # check if were accepted
        if "376" in resp:
            client.join_channel()
            print("joining channel {}".format(channel))

        
        # check if username is already used, if yes try username with _ (very shitty solution but it should work lol)
        if "433" in resp:
            username = "_" + username
            client.send_cmd("NICK", username)
            client.send_cmd("USER", "{} * * :{} ".format(username, username))

        # check if we joined
        if "366" in resp:
            joined = True


        if "PING" in resp:
            client.send_cmd("PONG", ":" + resp.split(":")[1])

        

    try:
        # stuff after joined
        while (cmd != "/quit"):
            cmd = input("< {}> ".format(username)).strip()
            if cmd == "/quit":
                quit()
            if cmd and len(cmd) > 0:
                client.send_message(cmd)
        
        
        response_thread = threading.Thread(target=print_response)
        response_thread.daemon = True
        response_thread.start()

    except KeyboardInterrupt:
        quit()

        t = threading.Thread(target=client.print_response())
        t.start()
