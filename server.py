
import time
from network import *
import select
import world

class Server:

    def __init__(self, ip, port, lvl):
        self.MAXPLAYERS = 1
        self.world = world.World(lvl)

        self.IP = ip
        self.PORT = port
        self.ADDR = (ip, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(self.ADDR)

        self.maybe_readable = [self.sock]
        self.maybe_writeable = []

        self.network_dict = {}
        self.client_input_table = {}
        self.sock.listen(self.MAXPLAYERS)

        self.data_table = {}

        self.new_clients = []

    def update(self):
        readable, writeable, exception = select.select(self.maybe_readable, self.maybe_writeable, self.maybe_readable)
        for s in readable:
            if s == self.sock:
                conn, addr = s.accept()
                conn.setblocking(0)
                self.maybe_readable.append(conn)
                self.maybe_writeable.append(conn)
                self.network_dict[conn] = Network(conn)
                self.world.add_new_player(conn, "car", 0, 0, 0)
                self.new_clients.append(conn)
                print(addr, "Connected!")
            else:
                msg = self.network_dict[s].receive_msg()
                self.client_input_table[s] = msg

        for s in writeable:
            if s in self.new_clients:
                pid = self.world.get_camera_for_player(s)
                gamestate = self.world.send_entire_gamestate()
                if pid is not None:
                    gamestate["CAM"] = pid
                self.network_dict[s].send_msg(gamestate)
                self.new_clients.remove(s)
            else:
                self.network_dict[s].send_msg(self.data_table)

        # Start updating world
        self.data_table = self.world.update(self.client_input_table)

