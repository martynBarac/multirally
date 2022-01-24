"""
For testing purposes,
displays the ping to pingpong_server
"""
from network import *
import time
import numpy as np
addr = socket.gethostbyname(socket.gethostname())
addr = addr.split(":")
if len(addr) > 1:
    PORT = int(addr[1])
else:
    PORT = 2302

IP = addr[0]

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
my_client = Network(sock)
my_client.connect(IP, PORT)
print("connected!")
action_number = 0
messages = []
times = []
latencies = []

while True:
    my_client.send_msg({"PING": action_number})
    action_number += 1
    messages.append(0)
    times.append(time.perf_counter())
    my_client.receive_msg()
    my_client.load_unread_messages()
    msg = my_client.read_oldest_message()
    if msg is not None:
        if msg["PONG"]:
            messages[msg["PONG"]] = 1
            latencies.append(time.perf_counter()-times[msg["PONG"]])
    print(len(messages)-np.sum(messages), np.average(latencies)*1000)



