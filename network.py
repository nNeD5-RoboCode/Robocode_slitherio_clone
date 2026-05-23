from contextlib import suppress

import socket
import threading
import time
import pyray as rl

MAX_MSG_SIZE = 2**13

class MessageSnake:
    def __init__(self):
        self.body_coords: list[rl.Vector2] = []
        self.radius = 0

def msg_to_snake(msg: str) -> MessageSnake:
    # "{radius}:{x} {y}, {x} {y}, {x} {y}, ..."
    msg_snake = MessageSnake()

    radius, body = msg.split(":")
    msg_snake.radius = float(radius)
    body = body.split(",")
    for i in range(len(body)):
        xy = body[i].split()
        coord = rl.Vector2(float(xy[0]), float(xy[1]))
        snake.body_coords.append(coord)

    return snake

def snake_to_msg(snake: MessageSnake) -> str:
    # "{radius}:{x} {y}, {x} {y}, {x} {y}, ..."
    msg = f"{snake.radius}:"
    for i, part in enumerate(snake.body_coords):
        if i < len(snake.body_coords) - 1:
            msg += f"{part.x:.2f} {part.y:.2f},"
        else:
            msg += f"{part.x:.2f} {part.y:.2f}"
    return msg




class Server:
    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port
        self.socket: socket.socket
        self.clients: [socket.socket] = []
        self.accept_loop_run  = False
        self.receive_loop_run = False

        self.buffers: dict[socket.socket, str] = {}
        self.snakes:  dict[socket.socket, MessageSnake] = {}

    def start(self):
        # TODO: try UDP instead of TCP
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
                self.buffers[sock] = ""
                self.snakes [sock] = MessageSnake()
                sock.send(f"id:{len(self.clients)}\n".encode())
                print("Someone Connected")
                time.sleep(0.1)

    def send_all(self, msg: str):
        msg += "\n"
        for client in self.clients:
            data = msg.encode()
            client.send(data )

    def receive_loop(self):
        while self.receive_loop_run:
            # "{radius}:{x} {y}, {x} {y}, {x} {y}, ..."
            with suppress(BlockingIOError):
                clients_to_remove = []
                for client in self.clients:
                    data = client.recv(MAX_MSG_SIZE)
                    if not data:
                        client.close()
                        clients_to_remove.append(client)
                        del self.buffers[client]
                        del self.snakes [client]
                        continue
                    msg = data.decode()
                    print(f"Server: {msg=}")
                    self.buffers[client] += msg

            is_anything_new = False
            for sock, buf in self.buffers.items():
                index = buf.find('\n')
                if index == -1:
                    continue
                snake = msg_to_snake(buf[0:index])
                self.snakes[sock] = snake
                self.buffers[sock] = buf[index + 1:-1]
                is_anything_new = True

            if is_anything_new:
                msg = ""
                for snake in self.snakes.values():
                    msg += snake_to_msg(snake)
                    msg += "@"

                self.send_all(msg)


class Client:
    def __init__(self):
        self.host: socket.socket
        self.buffer = ""

    def connect(self, ip: str, host: int):
        self.host = socket.create_connection((ip, host))
        self.host.setblocking(False)

    def send(self, msg: str):
        msg += '\n'
        if self.host != None:
            data = msg.encode()
            # TODO: check if is connected
            self.host.send(data)
        else:
            print(f"ERROR: Failed to send: host is '{self.host}'")

    def receive(self) -> str:
        # "{id}:?radius?:{x} {y}, {x} {y}, {x} {y}, ..."
        with suppress(BlockingIOError):
            data = self.host.recv(MAX_MSG_SIZE)
            if not data:
                return "serveroff"
            msg = data.decode()
            self.buffer += msg

        index = self.buffer.find("\n")
        if index == -1:
            return ""

        msg = self.buffer[0:index]
        self.buffer = self.buffer[index + 1:-1]
        return msg

