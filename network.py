import socket
import random
from player import Player

BUFFERSIZE = 500

HEAD_PINFO = "PINF"
HEAD_USERINFO = "UINF"
HEAD_PLAYERINPUT = "PINP"
HEAD_POWERINFO = "POWR"
TICKRATE = 30

class Network:
    def __init__(self, ip, port):
        self.IP = ip
        self.PORT = port
        self.ADDR = (ip, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


    def __del__(self):
        self.close()

    def send_msg_list(self, msg):
        """
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
        Returns a comma seperated message as a list
        """
        try:
            msg = self.sock.recv(BUFFERSIZE)
            msg = bytes_to_list(msg)
            if msg != []:
                return random.choice(msg) #We will have so many messages in the buffer! Just pick one from random to read.
            else:
                return ["NULL"]

        except BlockingIOError:
            return None, None

    def connect(self, host, port):
        self.sock.connect((host, port))

    def close(self):
        self.sock.close()


def decode_player_data(player, name, xpos, ypos, xvel, yvel, health, colour):
    """
    :param name: The default name
    :param player: The encoded player data
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

    pl = Player(xpos, ypos, name)
    pl.health = health
    pl.colour = colour
    pl.xvel = xvel
    pl.yvel = yvel
    return pl


def encode_player_data(pl, send_colour = False):
    """
    Converts player class into a list of variables
    """
    name = 'n'+pl.name
    xpos = 'x'+str(pl.xpos)
    ypos = 'y'+str(pl.ypos)
    xvel = 'X'+str(pl.xvel)
    yvel = 'Y'+str(pl.yvel)
    health = 'h'+str(pl.health)
    attributes = [HEAD_PINFO, name, xpos, ypos, xvel, yvel, health]
    if send_colour:
        colour = 'c'+encode_rgb(pl.colour)
        attributes.append(colour)
    _bytes = attributes
    return _bytes


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


