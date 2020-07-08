import socket
from player import Player

BUFFERSIZE = 48

HEAD_PINFO = "PINF"


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
        self.sock.send(msg)
        return None

    def recv_msg_list(self):
        """
        Returns a comma seperated message as a list
        """
        try:
            msg = self.sock.recv(BUFFERSIZE)
            msg = bytes_to_list(msg)
            return msg[0]

        except BlockingIOError:
            return None, None

    def connect(self, host, port):
        self.sock.connect((host, port))

    def close(self):
        self.sock.close()


def decode_player_data(player):
    _bytes = player.copy()

    attributes = _bytes
    if attributes[0] != HEAD_PINFO:
        print("decode_player_data: Could not decode data! ")
        return None

    name = attributes[1]
    xpos = float(attributes[2])
    ypos = float(attributes[3])
    health = int(attributes[4])
    pl = Player(xpos, ypos, name)
    pl.health = health
    return pl


def encode_player_data(pl):
    """
    Converts player class into a list of variables
    """
    name = pl.name
    xpos = str(pl.xpos)
    ypos = str(pl.ypos)
    health = str(pl.health)
    attributes = [HEAD_PINFO, name, xpos, ypos, health]
    _bytes = attributes
    return _bytes


def update_player_list(new_player, player_list):
    for i in range(len(player_list)):
        if player_list[i].name == new_player.name:
            player_list[i] = new_player
            return player_list

    if len(player_list) < 4:
        player_list.append(new_player)

    return player_list


def bytes_to_list(_bytes):
    _bytes = _bytes.decode()
    _bytes = _bytes.split(':')
    _list = []
    for m in _bytes:
        if m:
            _list.append(m.split(','))

    return _list
    return _list


def list_to_bytes(lst):
    """Convert a list of strings to bytes"""
    lst = ','.join(lst)
    lst = lst + ':'
    lst = lst.encode()
    return lst

"""
def make_list_string(lst):
    new_lst = []
    for item in lst:
        new_lst.append(str(item))
    return new_lst
"""
