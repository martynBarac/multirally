import socket


class serverSock:
    def __init__(self, ip, port):
        self.IP = ip
        self.PORT = port
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.sock.bind((self.IP, self.PORT))

    def __del__(self):
        self.close()

    def send_msg(self, msg, address):
        self.sock.sendto(msg, address)
        return None

    def recv_all(self):
        data, addr = self.sock.recvfrom(1024)
        print(data)
        return data, addr

    def recv_and_echo(self):
        received = self.recv_all()
        self.send_msg(received[0], received[1])
        return data, addr

    def close(self):
        self.sock.close()

user_choice = input("Send message Y/N? ")

if user_choice == "N":
    print("Initialising")
    my_server = serverSock("127.0.0.1", 27014)
    while True:
        print("working")
        print(my_server.recv_and_echo())

else:
    my_server = serverSock("127.0.0.1", 27014)
    message_to_send = input("Enter message: ")
    while message_to_send:
        my_server.send_msg(message_to_send.encode(), "127.0.0.1", 27014)
        message_to_send = input("Enter message: ")



