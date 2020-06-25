import socket
import time


class clientSock:
    def __init__(self, ip, port):
        self.IP = ip
        self.PORT = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.CONNECTION_TIMEOUT = 5
        self.sock.settimeout(1/60)

    def __del__(self):
        self.close()

    def send_msg(self, msg):
        self.sock.sendto(msg, (self.IP,self.PORT))
        return None

    def send_msg_handshake(self, msg):
        """
        Repeatedly sends the server a message until a handshake is received.
        Use this if a message needs to get across to the server reliably

        :param msg: The msg to send
        :return: Returns True if handshake successful
        """
        print("handshaking...")
        time_start = time.perf_counter()
        while True:
            self.sock.sendto(b'h,'+msg, (self.IP, self.PORT))
            try:
                received_message = self.receive_from_server()
                if received_message == b'h2,'+msg:
                    print("handshake successful")
                    return True
            except TimeoutError:
                pass
            time_end = time.perf_counter()
            duration = time_end-time_start
            if duration > self.CONNECTION_TIMEOUT:
                print("handshake error: timed out")
                return False

            time.sleep(1/60)

    def receive_from_server(self):
        """
        Will return a message if received
        Else will return empty string
        """
        try:
            msg, addr = self.sock.recvfrom(1024)
        except TimeoutError:
            msg = b''
        return msg

    def close(self):
        self.sock.close()


addr = input("Enter server address: ")
addr = addr.split(":")
if len(addr) > 1:
    PORT = int(addr[1])

else:
    PORT = 27014

IP = addr[0]

my_client = clientSock(IP, PORT)

message_to_send = input("Send a message: ")
while message_to_send:
    my_client.send_msg_handshake(message_to_send.encode())
    message_to_send = input("Send a message: ")