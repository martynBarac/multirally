import client2
import socket
import sys

if len(sys.argv) >= 2:
    addr = str(sys.argv[1])
else:
    addr = socket.gethostbyname(socket.gethostname())

addr = addr.split(":")
if len(addr) > 1:
    PORT = int(addr[1])
else:
    PORT = 2302

IP = addr[0]

my_client = client2.Client(IP, PORT)
my_client.main_loop()