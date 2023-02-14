import socket
import random
import json
import time

from player import Player
from powerup import Powerup

BUFFERSIZE = 1024

HEAD_PINFO = "PINF"
HEAD_USERINFO = "UINF"
HEAD_PLAYERINPUT = "PINP"
HEAD_POWERINFO = "POWR"
TICKRATE = 30
FAKE_LOSS_CHANCE = 0.00


class Network:
    def __init__(self, sock):

        self.sock = sock
        self.message_number = 0
        self.messages_to_send = []
        self.unread_messages = {}
        self.messages_to_read = {}
        self.start_time = time.perf_counter()
        self.bytes_recvd = 0

    def __del__(self):
        self.close()

    def receive_msg(self):
        # Simply recieve the message as a json string and return it
        try:
            msg_bytes, msg_addr = self.sock.recvfrom(BUFFERSIZE)
            msg_json = msg_bytes.decode()
            self.bytes_recvd += len(msg_bytes)
            if msg_addr in self.unread_messages:
                self.unread_messages[msg_addr] = self.unread_messages[msg_addr]+msg_json
            else:
                self.unread_messages[msg_addr] = msg_json
            return msg_json, msg_addr
        except BlockingIOError:
            return None, None

    def load_unread_messages(self, addr):
        # load the unread messages from json into a list

        if addr not in self.unread_messages:
            self.unread_messages[addr] = ""
            self.messages_to_read[addr] = []
        msg = self.unread_messages[addr]
        for i in range(len(msg)):
            msg2 = None
            # the very end of the string detected
            if i == len(msg)-1:
                msg2 = self.unread_messages[addr]


            elif i + 1 < len(msg):
                # End of the message detected
                if msg[i] + msg[i + 1] == "}{":
                    msg2 = self.unread_messages[addr][:i + 1]
            if msg2:
                try:
                    self.messages_to_read[addr].append(json.loads(msg2)) # Try to load it
                    if i == len(msg): self.unread_messages[addr] = ""
                    else: self.unread_messages[addr] = self.unread_messages[addr][i + 1:] # We read the message so forget it
                except json.decoder.JSONDecodeError:
                    #print("JsonerrorSUM", msg) # wtf
                    break

    def add_client(self, addr):
        self.messages_to_read[addr] = []
        self.unread_messages[addr] = ""

    def read_oldest_message(self, addr):
        msg = 0
        if self.messages_to_read[addr]:
            temp = self.messages_to_read[addr].copy()
            msg = temp[0]
            self.messages_to_read[addr].pop(0)

        return msg

    def send_msg(self, message, addr):
        randchance = random.uniform(0, 1)
        if randchance < FAKE_LOSS_CHANCE:
            return
        msg_json = json.dumps(message)
        msg_json = "".join(msg_json.split())
        #msg_json = "".join(msg_json.split("\""))
        msg_bytes = msg_json.encode()
        sent_bytes = 0
        msg_length = len(msg_bytes)
        while msg_length > sent_bytes:

            sent = self.sock.sendto(msg_bytes[sent_bytes:], addr)
            if sent == 0:
                raise RuntimeError("socket connection broken")
            sent_bytes += sent


    def send_ack(self, n):
        message = ("ACK", n)
        self.send_msg(message)

    def send_msg_list(self, msg):
        """
        LEGACY FUNCTION
        Input a list of strings as a message
        """
        msg = list_to_bytes(msg)
        msg_length = len(msg)
        sent_bytes = 0
        while msg_length > sent_bytes:
            sent = self.sock.send(msg[sent_bytes:]) #Send the unsent parts of the message
            if sent == 0:
                raise RuntimeError("socket connection broken")
            sent_bytes += sent

        return None

    def recv_msg_list(self):
        """
        LEGACY FUNCTION
        Returns a comma seperated message as a list
        """
        try:
            msg = self.sock.recv(BUFFERSIZE)
            msg = bytes_to_list(msg)
            if msg != []:
                # We will have so many messages in the buffer! Just pick one from random to read.
                return random.choice(msg)
            else:
                return ["NULL"]

        except BlockingIOError:
            return None, None

    def connect(self, host, port):
        self.sock.connect((host, port))

    def close(self):
        self.sock.close()


def decode_player_data(player, name, angle, xpos, ypos, xvel, yvel, health, colour):
    """
    LEGACY FUNCTION
    :param name: The default name
    :param player: The encoded player data
    :param angle: angle
    :param xpos: The default xposition if position data was not recieved
    :param ypos: The default yposition if position data was not recieved
    :param health: The default health if health data was not recieved
    :param colour: The default colour if colour data was not recieved
    :return: The player object built from the encoded data
    """
    _bytes = player.copy()

    attributes = _bytes
    if attributes[0] != HEAD_PINFO:
        print("decode_player_data: Could not decode data! ")
        return None

    for i in range(1, len(attributes), 1):
        head = attributes[i][0]
        updated_colour = False
        if head == 'n':
            name = attributes[i][1:]
        elif head == 'x':
            xpos = float(attributes[i][1:])
        elif head == 'y':
            ypos = float(attributes[i][1:])
        elif head == 'X':
            xvel = float(attributes[i][1:])
        elif head == 'Y':
            yvel = float(attributes[i][1:])
        elif head == 'h':
            health = int(attributes[i][1:])
        elif head == 'c':
            colour = decode_rgb(attributes[i][1:])
        elif head == 'a':
            angle = float(attributes[i][1:])

    pl = Player(xpos, ypos, angle, name)
    pl.health = health
    pl.colour = colour
    pl.xvel = xvel
    pl.yvel = yvel
    return pl


def encode_player_data(pl, send_colour = False):
    """
    Converts player class into a list of variables
    LEGACY FUNCTION
    """
    name = 'n'+pl.name
    xpos = 'x'+str(pl.xpos)
    ypos = 'y'+str(pl.ypos)
    xvel = 'X'+str(pl.xvel)
    yvel = 'Y'+str(pl.yvel)
    health = 'h'+str(pl.health)
    angle = 'a'+str(pl.angle)
    attributes = [HEAD_PINFO, name, xpos, ypos, angle, xvel, yvel, health]
    if send_colour:
        colour = 'c'+encode_rgb(pl.colour)
        attributes.append(colour)
    _bytes = attributes
    return _bytes


def encode_powerup_data(powerups):
    powmsg = [HEAD_POWERINFO]
    for i in range(len(powerups)):
        x = str(i)+"/x"+str(powerups[i].xpos)
        y = str(i)+"/y"+str(powerups[i].ypos)
        typ = str(i)+"/t"+str(powerups[i].type)
        powmsg.append(x)
        powmsg.append(y)
        powmsg.append(typ)

    return list_to_bytes(powmsg)


def decode_powerup_data(msg):
    decoded = []
    powdict = {} # A single item will look like id:[x, y, type]

    for att in msg[1:]:
        att = att.split("/")
        idd = att[0] # an id is used for each attribute so the order of the list doesnt matter
        powdict.setdefault(idd, [0, 0, 0])
        if att[1][0] == "x":
            powdict[idd][0] = int(att[1][1:])
        if att[1][0] == "y":
            powdict[idd][1] = int(att[1][1:])
        if att[1][0] == "t":
            powdict[idd][2] = int(att[1][1:])
    for po in powdict.values():
        decoded.append(Powerup(po[0], po[1], po[2]))

    return decoded


def update_existing_player(new_player_data, existing_player):
    new_player = decode_player_data(new_player_data,
                                    existing_player.name,
                                    existing_player.xpos,
                                    existing_player.ypos,
                                    existing_player.angle,
                                    existing_player.xvel,
                                    existing_player.yvel,
                                    existing_player.health,
                                    existing_player.colour
                                    )
    return new_player


def return_error_player(msg):
    return decode_player_data(msg, "ERR", 32, 32, 0, 0, 0, 100, (255, 255, 255))


def encode_action_data(actions):
    """
    Action list input dict is {UP:BOOL,LEFT:BOOL,RIGHT:BOOL, DOWN:BOOL}
    Action list output is [up,left,right,down]
    """
    action_list = [HEAD_PLAYERINPUT]
    for action in actions:
        action_list.append(str(actions[action]))
    return action_list


def decode_action_data(actions):
    """Inverse of encode_action_data"""
    action_dict = {1: False, 2: False, 3: False, 4: False}

    for i in range(1,5,1):
        if actions[i] == "True":
            action_dict[i] = True

    return action_dict


def update_player_list(new_player, player_list):
    for i in range(len(player_list)):
        if player_list[i].name == new_player.name:
            player_list[i] = new_player
            return player_list

    if len(player_list) < 4:
        player_list.append(new_player)

    return player_list


COL_DICT = {'a': 0, 'b': 50, 'c': 100, 'd': 150, 'e': 200, 'f': 250}


def decode_rgb(code):
    if len(code) != 3:
        print("BAD CODE!")
        return (255, 255, 255)
    r = COL_DICT[code[0]]
    g = COL_DICT[code[1]]
    b = COL_DICT[code[2]]
    return (r, g, b)


def encode_rgb(rgb):
    letters = ['a', 'a', 'a']
    for i in range(len(rgb)):
        for col_letter in COL_DICT:
            if abs(rgb[i] - COL_DICT[col_letter]) < 25:
                letters[i] = col_letter
    return letters[0]+letters[1]+letters[2]


def find_player_from_name(player_name, player_list):
    found_player = None
    for player in player_list:
        if player.name == player_name:
            found_player = player
    return found_player


def bytes_to_list(_bytes):
    _bytes = _bytes.decode()
    _bytes = _bytes.split(':')
    _list = []
    for m in _bytes:
        if m:
            _list.append(m.split(','))
    return _list


def list_to_bytes(lst):
    """Convert a list of strings to bytes"""
    lst = ','.join(lst)
    lst = lst + ':'
    lst = lst.encode()
    return lst


