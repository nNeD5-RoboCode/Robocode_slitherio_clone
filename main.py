#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["raylib"]
# ///

# TODO: add sounds
from enum import Enum
from contextlib import suppress

import socket
import threading

import pyray as rl

class Button:
    def __init__(self, rect: rl.Rectangle, texture: rl.Texture2D):
        self.rect       = rect
        self.texture    = texture
        self.is_hovered = False
        self.is_pressed = False

    def draw(self):
        self._update()
        src_rect = rl.Rectangle(0, 0, self.texture.width, self.texture.height)
        color = rl.WHITE
        if self.is_hovered: color = rl.LIGHTGRAY
        if self.is_pressed: color = rl.GRAY
        rl.draw_texture_pro(self.texture, src_rect, self.rect, [0, 0], 0, color)

    def _update(self):
        if rl.check_collision_point_rec(rl.get_mouse_position(), self.rect):
            self.is_hovered = True
            if rl.is_mouse_button_down(rl.MOUSE_LEFT_BUTTON):
                self.is_pressed = True
            else:
                self.is_pressed = False
        else:
            self.is_hovered = False
            self.is_pressed = False

    def is_clicked(self) -> bool:
        if rl.is_mouse_button_released(rl.MOUSE_LEFT_BUTTON) and self.is_hovered:
            return True
        return False

class InputBox:
    def __init__(self, rect: rl.Rectangle):
        self.rect = rect
        self.text = ""
        self.is_hovered = False
        self.is_focused = False
        self.max_chars = 15

    def draw(self):
        self._update()
        rl.draw_rectangle_rounded(self.rect, 0.2, 10, rl.DARKGRAY)
        border_color = rl.GREEN if self.is_focused else rl.LIGHTGRAY
        rl.draw_rectangle_rounded_lines_ex(self.rect, 0.2, 10, 5, border_color)
        font_size = 30
        text_x = int(self.rect.x + 10)
        text_y = int(self.rect.y + (self.rect.height - font_size) / 2)
        rl.draw_text(self.text, text_x, text_y, font_size, rl.WHITE)
        if self.is_focused:
            if (int(rl.get_time() * 2) % 2) == 0:
                text_width = rl.measure_text(self.text, font_size)
                rl.draw_text("|", text_x + text_width + 2, text_y, font_size, rl.WHITE)


    def is_accepted(self) -> bool:
        return self.is_focused and rl.is_key_released(rl.KEY_ENTER)

    def _update(self):
        if rl.check_collision_point_rec(rl.get_mouse_position(), self.rect):
            self.is_hovered = True
            rl.set_mouse_cursor(rl.MOUSE_CURSOR_IBEAM)
        else:
            self.is_hovered = False
            rl.set_mouse_cursor(rl.MOUSE_CURSOR_DEFAULT)

        if rl.is_mouse_button_pressed(rl.MOUSE_LEFT_BUTTON):
            self.is_focused = self.is_hovered

        if self.is_focused:
            key = rl.get_char_pressed()
            while key > 0:
                if (key >= 32) and (key <= 125) and (len(self.text) < self.max_chars):
                    self.text += chr(key)
                key = rl.get_char_pressed()

            if rl.is_key_pressed(rl.KEY_BACKSPACE):
                if len(self.text) > 0:
                    self.text = self.text[:-1]

class Server:
    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port
        self.socket: socket.socket = socket.create_server((ip, port))
        self.socket.setblocking(False)

        self.clients: [socket.socket] = []

        # TODO: make method to delete server cleanly
        self.accept_thread   = threading.Thread(target=self.accept_loop)
        self.receive_thread  = threading.Thread(target=self.receive_loop)

        self.accept_thread.start()
        self.receive_thread.start()


    def accept_loop(self):
        while True:
            with suppress(BlockingIOError):
                socket, _ = self.socket.accept()
                socket.setblocking(False)
                self.clients.append(socket)

    def send_all(self, msg: str):
        for client in self.clients:
            data = msg.encode()
            client.send(data)

    def receive_loop(self):
        while True:
            # "{id}:?radius?:{x} {y}, {x} {y}, {x} {y}, ..."
            with suppress(BlockingIOError):
                for client in self.clients:
                    data = client.recv(1024) # TODO: max valued based on lenght limit
                    # TODO: disconnet clinent
                    msg = data.decode()
                    print(msg)
                    self.send_all(msg)


class Client:
    def __init__(self):
        self.host: socket.socket

    def connect(self, ip: str, host: int):
        self.host = socket.create_connection((ip, host))

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

class GameState(Enum):
    MENU     = 1,
    HOST     = 2,
    JOIN     = 3,
    GAME     = 4,
    INPUT_IP = 5,

BG_COLOR = rl.Color(24, 24, 24, 255)
game_state = GameState.MENU

rl.set_config_flags(rl.ConfigFlags.FLAG_WINDOW_RESIZABLE)
rl.init_window(16*100, 9*100, "Slitherio")

IMAGES = {
    "host": rl.load_texture("host.png"),
    "join": rl.load_texture("join.png"),
    "menu": rl.load_texture("menu.png"),
    "play": rl.load_texture("play.png"),
}


btn_host = Button(rl.Rectangle(600, 0, 400, 200),    IMAGES["host"])
btn_join = Button(rl.Rectangle(600, 450, 400, 200),  IMAGES["join"])
btn_menu = Button(rl.Rectangle(1100, 100, 657, 380), IMAGES["menu"])
btn_play = Button(rl.Rectangle(600, 650, 400, 200),  IMAGES["play"])
input_ip = InputBox(rl.Rectangle(600, 600, 350, 60))

server: Server|None = None
client: Client|None = None

while not rl.window_should_close():
    rl.begin_drawing()
    rl.clear_background(BG_COLOR)

    match game_state:
        case GameState.MENU:
            btn_host.draw()
            btn_join.draw()
            if btn_host.is_clicked():
                print("host")
                game_state = GameState.HOST
            if btn_join.is_clicked():
                print("join")
                game_state = GameState.JOIN

        case GameState.HOST:
            font_size = 64
            local_ip = socket.gethostbyname(socket.gethostname())
            text_size = rl.measure_text(local_ip, font_size)
            rl.draw_text(f"IP: {local_ip}",
                         rl.get_render_width() // 2 - text_size // 2,
                         rl.get_render_height() // 2 - font_size // 2,
                         font_size,
                         rl.SKYBLUE)
            # TODO: draw how many clients are connected?
            if server == None:
                server = Server(local_ip, 6667)

            btn_menu.draw()
            btn_play.draw()
            if btn_menu.is_clicked():
                game_state = GameState.MENU
                print("menu")
            if btn_play.is_clicked():
                game_state = GameState.GAME
                print("Game")


        case GameState.JOIN:
            rl.draw_text("Write Yours IP:", 600, 550, 32, rl.BLUE)
            btn_menu.draw()
            input_ip.draw()
            if btn_menu.is_clicked():
                game_state = GameState.MENU
            if input_ip.is_accepted():
                print(input_ip.text)
                client = Client()
                client.connect(input_ip.text, 6667)

        case GameState.GAME:
            assert(not (server == None and client == None))
            assert(not (server != None and client != None))
            if client:
                client.send("PIP")



    rl.end_drawing()

rl.close_window()
