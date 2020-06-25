import socket


class serverSock:
    def __init__(self, ip, port):
        self.IP = ip
        self.PORT = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.IP, self.PORT))

    def __del__(self):
        self.close()

    def send_msg(self, msg, addr):
        self.sock.sendto(msg, addr)
        return None

    def recv_all(self):
        msg, addr = self.sock.recvfrom(1024)
        return msg, addr


    def recv_and_handshake(self):
        """
        Recieves and returns message, will handshake if asked.

        :return: returns messgae and adress from the client that sent a message
        """
        msg, addr = self.recv_all()
        msg = msg.split(b',')

        # If the message begins with h then the client wants a handshake
        # echo it back for a handshake
        if msg[0] == b'h':
            print("Handshaking..")
            new_msg = b'h2,'+b','.join(msg[1:])
            self.send_msg(new_msg, addr)

        return msg, addr

    def close(self):
        self.sock.close()



print("Initialising")
my_server = serverSock("127.0.0.1", 27014)
while True:
    print(my_server.recv_and_handshake()[0])
