
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
        self.client_last_action_number = {}
        self.sock.listen(self.MAXPLAYERS)

        self.data_table = {}

        self.new_clients = []
        self.start_time = 0

    def update(self):
        readable, writeable, exception = select.select(self.maybe_readable, self.maybe_writeable, self.maybe_readable)
        for s in readable:
            if s == self.sock:
                conn, addr = s.accept()
                conn.setblocking(0)
                self.maybe_readable.append(conn)
                self.maybe_writeable.append(conn)
                self.network_dict[conn] = Network(conn)
                self.world.add_new_player(conn, "car")
                self.new_clients.append(conn)
                print(addr, "Connected!")
            else:
                try:
                    self.network_dict[s].receive_msg() # Get the client inputs
                    self.network_dict[s].load_unread_messages()
                    while True:
                        msg = self.network_dict[s].read_oldest_message()
                        if msg is None:
                            break
                        self.client_input_table[s] = msg
                        self.client_last_action_number[s] = msg['a']
                except (ConnectionResetError, ConnectionAbortedError):
                    del(self.network_dict[s])
                    self.maybe_readable.remove(s)
                    self.maybe_writeable.remove(s)
                    writeable.remove(s)
                    self.world.destroy_player(s)

        for s in writeable:
            if s in self.new_clients:
                pid = self.world.get_camera_for_player(s)
                gamestate = self.world.send_entire_gamestate(s)
                if pid is not None:
                    gamestate["CAM"] = pid
                gamestate["LEV"] = self.world.level_name
                self.network_dict[s].send_msg(gamestate)
                self.new_clients.remove(s)
            else:
                if s in self.data_table:
                    if s in self.client_last_action_number:
                        self.data_table[s]["ACT"] = self.client_last_action_number[s]
                    self.network_dict[s].send_msg(self.data_table[s])


        # Start updating world
        self.data_table = self.world.update(self.client_input_table) # big slow update

        time_elapsed = time.perf_counter() - self.start_time
        self.world.dt = (time_elapsed) * 10
        self.start_time = time.perf_counter()

        time.sleep(max(1 / 8 - time.perf_counter()+self.start_time, 0))



