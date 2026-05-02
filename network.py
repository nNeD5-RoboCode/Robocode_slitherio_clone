from contextlib import suppress

import socket
import threading

class Server:
    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port
        self.socket: socket.socket
        self.clients: [socket.socket] = []
        self.accept_loop_run  = False
        self.receive_loop_run = False

    def start(self):
        self.socket: socket.socket = socket.create_server((self.ip, self.port))
        self.socket.setblocking(False)

        self.accept_thread  = threading.Thread(target=self.accept_loop)
        self.receive_thread = threading.Thread(target=self.receive_loop)

        self.accept_loop_run  = True
        self.receive_loop_run = True

        self.accept_thread.start()
        self.receive_thread.start()

    def finish(self):
        self.accept_loop_run  = False
        self.receive_loop_run = False
        self.accept_thread.join()
        self.receive_thread.join()

    def accept_loop(self):
        while self.accept_loop_run:
            with suppress(BlockingIOError):
                sock, _ = self.socket.accept()
                sock.setblocking(False)
                self.clients.append(sock)
                sock.send(f"id:{len(self.clients)}".encode())
                print("Someone Connected")

    def send_all(self, msg: str):
        for client in self.clients:
            data = msg.encode()
            client.send(data)

    def receive_loop(self):
        while self.receive_loop_run:
            # "{id}:?radius?:{x} {y}, {x} {y}, {x} {y}, ..."
            with suppress(BlockingIOError):
                print(f"Client number: {len(self.clients)}")
                for client in self.clients:
                    data = client.recv(1024) # TODO: max valued based on lenght limit
                    # TODO: disconnet clinent
                    msg = data.decode()
                    print(f"Server: {msg=}")
                    self.send_all(msg)


class Client:
    def __init__(self):
        self.host: socket.socket

    def connect(self, ip: str, host: int):
        self.host = socket.create_connection((ip, host))
        self.host.setblocking(False)

    def send(self, msg: str):
        if self.host != None:
            data = msg.encode()
            # TODO: check if is connected
            self.host.send(data)
        else:
            print(f"ERROR: Failed to send: host is '{self.host}'")

    def receive(self) -> str:
        # "{id}:?radius?:{x} {y}, {x} {y}, {x} {y}, ..."
        with suppress(BlockingIOError):
            data = self.host.recv(1024) # TODO: max valued based on lenght limit
            # TODO: disconnet clinent
            msg = data.decode()
            return msg
        return ""

