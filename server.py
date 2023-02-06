
import time

import constant
from network import *
import select
import world
import threading


class Server:
    def __init__(self, ip, port, lvl):
        self.MAXPLAYERS = 1
        self.world = world.World(lvl)

        self.IP = ip
        self.PORT = port
        self.ADDR = (ip, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(self.ADDR)
        self.net_server = Network(self.sock)
        self.sock.setblocking(0)

        self.maybe_readable = [self.sock]
        self.maybe_writeable = []

        self.network_dict = {}
        self.client_input_table = {}
        self.client_last_action_number = {}

        self.data_table = {}

        self.new_clients = []
        self.connected_clients = []
        self.start_time = 0
        self.tick_number = 0

        # What number is the latest message for that client
        self.message_number_for_client = {}

        # Keep track of what message number the client is up to
        self.client_unacked_messages = {}
        self.client_last_acked_message = {}

        self.read_thread = threading.Thread(target=self.read_client_messages)
        self.read_thread.daemon = True
        self.read_thread.start()

    def update(self):
        # Recieve messages from clients
        # Apply controls to player
        # Update last read message for that client
        for addr in self.connected_clients:
                #self.client_last_action_number[addr] = msg['a']
            # Send messages to clients
            if addr in self.new_clients:
                pid = self.world.get_camera_for_player(addr)
                gamestate = self.world.send_entire_gamestate(addr)
                if pid is not None:
                    gamestate["CAM"] = pid
                gamestate["LEV"] = self.world.level_name
                self.message_number_for_client[addr] = 0
                self.client_unacked_messages[addr] = {}
                self.client_last_acked_message[addr] = 0
                gamestate["N"] = [self.message_number_for_client[addr], 0, 0]
                self.net_server.send_msg(gamestate, addr)
                self.new_clients.remove(addr)
                print(addr, "connected")
            else:
                if addr in self.data_table:
                    if addr in self.client_last_action_number:
                        self.data_table[addr]["ACT"] = self.client_last_action_number[addr]
                    self.message_number_for_client[addr] += 1
                    self.data_table[addr]["N"] = [self.message_number_for_client[addr], self.client_last_acked_message[addr], self.tick_number]
                    for msgnum in self.client_unacked_messages[addr]:
                        if self.message_number_for_client[addr] - msgnum >= 2:
                            print("not acked", msgnum)
                            self.net_server.send_msg(self.client_unacked_messages[addr][msgnum])
                    self.net_server.send_msg(self.data_table[addr], addr)

        # Start updating world
        self.data_table = self.world.update(self.client_input_table)  # big slow update

        time_elapsed = time.perf_counter() - self.start_time
        self.world.dt = (1 / constant.TICKRATE) * 10


        time.sleep(max(1 / constant.TICKRATE - time_elapsed, 0))
        self.start_time = time.perf_counter()
        return

    def read_client_messages(self):
        # Get messages from clients
        print("STARTED THREAD")
        while True:
            try:
                msg, addr = self.net_server.receive_msg()

            except ConnectionResetError:
                msg = None
                addr = None
                pass

            if addr not in self.connected_clients and addr is not None:
                self.world.add_new_player(addr, "car")
                self.new_clients.append(addr)
                self.connected_clients.append(addr)
                self.net_server.add_client(addr)

            for addr in self.connected_clients:
                self.net_server.load_unread_messages(addr)
                while True:
                    msg = self.net_server.read_oldest_message(addr)
                    if msg == 0:
                        break

                    if 'N' in msg:
                        for i in msg['N']:
                            i = str(i)
                            self.client_last_acked_message[addr] = max(self.client_last_acked_message[addr], int(i, 16))
                            if int(i, 16) in self.client_unacked_messages:
                                del (self.client_unacked_messages[int(i, 16)])
                    else:
                        self.client_input_table[addr] = msg

    def send_message_to_client(self, msg, addr):
        self.message_number_for_client[addr] += 1
        self.net_server.send_msg(msg, addr)
        self.client_unacked_messages[addr][self.message_number_for_client] = self.only_important_info(msg)

    def only_important_info(self, msg):
        """
        Only some information in a message needs to be sent reliably
        """
        newmsg = {}
        newmsg["NEW"] = msg["NEW"]
        newmsg["DEL"] = msg["DEL"]
        newmsg["CAM"] = msg["CAM"]
        newmsg["LEV"] = msg["LEV"]
        return newmsg


        # Start updating world
        self.data_table = self.world.update(self.client_input_table) # big slow update

        time_elapsed = time.perf_counter() - self.start_time
        self.world.dt = (time_elapsed) * 10
        self.start_time = time.perf_counter()
        delay = max(1 / constant.TICKRATE - time_elapsed, 0)
        if delay == 0:
            print("TICK SKIP SERVER IS SLOW")
        time.sleep(delay)
