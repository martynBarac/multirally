"""
For testing purposes,
Pongs to the client after recieving a ping
"""

import time
from network import *
import select

class Server:

    def __init__(self, ip, port):
        self.MAXPLAYERS = 1

        self.IP = ip
        self.PORT = port
        self.ADDR = (ip, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(self.ADDR)

        self.maybe_readable = [self.sock]
        self.maybe_writeable = []

        self.network_dict = {}
        self.client_input_table = {}
        self.client_last_action_number = {}
        self.sock.listen(self.MAXPLAYERS)

        self.new_clients = []
        self.start_time = 0

    def update(self):
        readable, writeable, exception = select.select(self.maybe_readable, self.maybe_writeable, self.maybe_readable)
        for s in readable:
            if s == self.sock:
                conn, addr = s.accept()
                #conn.setblocking(0)
                self.maybe_readable.append(conn)
                self.maybe_writeable.append(conn)
                self.network_dict[conn] = Network(conn)
                print(addr, "Connected!")
            else:
                try:
                    self.network_dict[s].receive_msg()
                    self.network_dict[s].load_unread_messages()
                    while True:
                        msg = self.network_dict[s].read_oldest_message()
                        if msg is None:
                            break
                        self.client_input_table[s] = msg
                        self.client_last_action_number[s] = msg['PING']
                except ConnectionResetError:
                    del(self.network_dict[s])
                    self.maybe_readable.remove(s)
                    self.maybe_writeable.remove(s)
                    writeable.remove(s)

        for s in writeable:
            self.network_dict[s].send_msg({"PONG":self.client_last_action_number[s]})
            pass


server = Server(socket.gethostbyname(socket.gethostname() ), 2302)
while True:
    server.update()
    time.sleep(1 / 64)