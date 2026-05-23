#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["raylib"]
# ///

# TODO: add sounds
from enum import Enum

import socket

import pyray as rl

from ui      import Button, InputBox
from network import Server, Client
from snake   import game


class GameState(Enum):
    MENU = 1,
    HOST = 2,
    JOIN = 3,
    WAIT = 4,
    GAME = 5,


def main():
    BG_COLOR = rl.Color(24, 24, 24, 255)
    game_state = GameState.MENU
    win_width  = 16 * 100
    win_height =  9 * 100
    rl.set_config_flags(rl.ConfigFlags.FLAG_WINDOW_RESIZABLE)
    rl.init_window(win_width, win_height, "Slitherio")

    IMAGES = {
        "host": rl.load_texture("host.png"),
        "join": rl.load_texture("join.png"),
        "menu": rl.load_texture("menu.png"),
        "play": rl.load_texture("play.png"),
    }


    btn_host = Button(rl.Rectangle(  600,   0,   400, 200),  IMAGES["host"], win_width, win_height)
    btn_join = Button(rl.Rectangle(  600,   450, 400, 200),  IMAGES["join"], win_width, win_height)
    btn_menu = Button(rl.Rectangle(  2,     10,  329, 190),  IMAGES["menu"], win_width, win_height)
    btn_play = Button(rl.Rectangle(  600,   450, 400, 200),  IMAGES["play"], win_width, win_height)
    input_ip = InputBox(rl.Rectangle(600,   600, 350, 60),  win_width, win_height)

    server: Server|None = None
    client: Client|None = None

    client_id = None

    src_rec      = rl.Rectangle(0, 0, win_width, -win_height)
    menu_texture = rl.load_render_texture(win_width, win_height)

    while not rl.window_should_close():
        rl.begin_texture_mode(menu_texture)

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
                             win_width // 2 - text_size // 2 - 50,
                             win_height // 2 - font_size // 2 - 200,
                             font_size,
                             rl.SKYBLUE)
                if server == None:
                    # TODO: finish and delete server if come back to menu
                    server = Server(local_ip, 6667)
                    server.start()

                    # TODO: host should have game as well
                    # client = Client()
                    # client.connect(local_ip, 6667)

                btn_menu.draw()
                btn_play.draw()
                if server:
                    rl.draw_text(f"Players: {len(server.clients)}", 100, 100, 64, rl.WHITE)
                if btn_menu.is_clicked():
                    game_state = GameState.MENU
                    print("menu")
                if btn_play.is_clicked():
                    server.send_all("start")
                    game_state = GameState.GAME
                    print("Game")


            case GameState.JOIN:
                rl.draw_text("Write Yours IP:", 600, 550, 32, rl.BLUE)
                btn_menu.draw()
                input_ip.draw()
                if btn_menu.is_clicked():
                    game_state = GameState.MENU
                if input_ip.is_accepted():
                    client = Client()
                    client.connect(input_ip.text, 6667)
                if client:
                    msg = client.receive()
                    if "id:" in msg:
                        client_id = msg.split(":")[1]
                        client_id = int(client_id)
                        game_state = GameState.WAIT

            case GameState.WAIT:
                rl.draw_text("Waiting for host to start game", 400, 500, 65, rl.WHITE)
                msg = client.receive()
                if msg == "start":
                    game_state = GameState.GAME

            case GameState.GAME:
                assert(not (server == None and client == None))
                assert(not (server != None and client != None))
                if client:
                    game(client_id, client)

        rl.end_texture_mode()

        rl.begin_drawing()
        dst_rec = rl.Rectangle(0, 0, rl.get_render_width(), rl.get_render_height())
        rl.draw_texture_pro(
            menu_texture.texture,
            src_rec,
            dst_rec,
            rl.vector2_zero(),
            0,
            rl.WHITE,
        )
        rl.end_drawing()

    rl.close_window()
    if server: server.finish()

if __name__ == "__main__":
    main()
