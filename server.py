
import time
from network import *
import select
import world


class Server:

    def __init__(self, ip, port):
        self.MAXPLAYERS = 1
        self.world = world.World

        self.IP = ip
        self.PORT = port
        self.ADDR = (ip, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(self.ADDR)

        self.maybe_readable = [self.sock]
        self.maybe_writeable = []

        self.network_dict = {}
        self.sock.listen(self.MAXPLAYERS)

    def update(self):
        readable, writeable, exception = select.select(self.maybe_readable, self.maybe_writeable, self.maybe_readable)
        for s in readable:
            if s == self.sock:
                conn, addr = s.accept()
                conn.setblocking(0)
                self.maybe_readable.append(conn)
                self.maybe_writeable.append(conn)
                self.network_dict[conn] = Network(conn)
                print(addr, "Connected!")
            else:
                msg = self.network_dict[s].receive_msg()
                print(msg)

        for s in writeable:
            self.network_dict[s].send_msg({1: "John"})