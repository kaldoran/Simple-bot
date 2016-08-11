import re
import socket
import opendht

server = 'irc.freenode.net'
channel = '#opendht'
nick = 'OpenDhtBot'
port = 6667

# Some actions to connect to the Dht
node = opendht.DhtRunner()
node.run()

node.bootstrap("bootstrap.ring.cx", "4222")

# Socket that connect to the irc chat
ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ircsock.connect((server, port))

handle = ircsock.makefile(mode='rw', buffering=1, encoding='utf-8', newline='\r\n')

# List of simple command in a file
clist = {}
with open("command_list.txt") as f:
    for line in f:
        if line[0] != "#":
            (key, val) = line.split(" ", 1)
            clist[key] = val

# Choose nickname
print('NICK', nick, file=handle)

# Register to irc freenode
print('USER', nick, nick, nick, ': Bot de test', file=handle)

# Join the channel
print('JOIN', channel, file=handle)

# Send a message in the channel
def message(msg):
    print("PRIVMSG", channel, ":",msg, file=handle)

# Send message to user
def privmessage(user, msg):
    print(":source PRIVMSG", user, ":",msg, file=handle)

for line in handle:
    line = line.strip()
    print(line)

    # Reply to serveur ping
    if "PING" in line:
        print("PONG :" + line.split(':')[1], file=handle)
    else:
        usr = line.split(" ", 3)
 
        ruser    = re.search(r':([^!]*)!.*', usr[0])
        if ruser:
            iuser = ruser.group(1)

        iaction  = usr[1] 
        ichannel = usr[2]
        if iaction == "PRIVMSG":
            if ichannel == channel: 
                imsg     = usr[3]
                if usr[3][1] == '!':
                    icommand = imsg.strip(':').strip('!').split(" ")
                    
                    # If the command is in the dictionnary created by the file :
                    if icommand[0] in clist:
                        message(clist[icommand[0]])
                    else:
                        # Get on the DHT
                        if icommand[0] == "get":
                            if len(icommand) < 2:
                                message("get <where>")
                            else:
                                results = node.get(opendht.InfoHash.get(icommand[1]))
                                for r in results:
                                    message(r)
                        # Put on the Dht
                        elif icommand[0] == "put":
                            if len(icommand) < 3:
                                message("put <where> <value>")
                            else:
                                node.put(opendht.InfoHash.get(icommand[1]), opendht.Value(icommand[2].encode()))
                        # Hash the input (sha1)
                        elif icommand[0] == "hash":
                            if len(icommand) < 2:
                                message("hash <value>")
                            else:
                                message(opendht.InfoHash.get(icommand[1]))
                        else:    
                            message(iuser + " the command '" + icommand[0] + "' is not implemented yet [WIP].")
            else:
                # If user msg the bot
                privmessage(iuser, "Sorry i hate private message")
