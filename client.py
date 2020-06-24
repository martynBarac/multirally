import socket


class clientSock:
    def __init__(self, ip, port):
        self.IP = ip
        self.PORT = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def __del__(self):
        self.close()

    def send_msg(self, msg, address):
        self.sock.sendto(msg, address)
        return None

    def recieve_from_server(self):
        message = self.sock.recvfrom(1024)
        return message[0]

    def close(self):
        self.sock.close()

my_client = clientSock("127.0.0.1", 27014)

message_to_send = input("Send a message: ")
while message_to_send:
    my_client.send_msg(message_to_send.encode(), ("127.0.0.1", 27014))
    print(my_client.recieve_from_server())
    message_to_send = input("Send a message: ")