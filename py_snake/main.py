#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["raylib", "numpy"]
# ///


from dataclasses import dataclass
import random
import pyray as rl


@dataclass(kw_only=True)
class Snake:
    color    : rl.Color
    radius   : int
    speed    : int
    head     : rl.Vector2
    body     : list[rl.Vector2]

def draw_snake(snake: Snake):
    outline_color = rl.SKYBLUE
    rl.draw_circle_v(snake.head, snake.radius, snake.color)
    rl.draw_poly_lines_ex(snake.head, 100, snake.radius, 0, 3, outline_color)
    for c in snake.body:
        rl.draw_circle_v(c, snake.radius, snake.color)
        rl.draw_poly_lines_ex(c, 100, snake.radius, 0, 3, outline_color)

def move_snake_to(snake: Snake, pos: rl.Vector2) -> Snake:
    # move head
    snake.head = rl.vector2_move_towards(snake.head, pos, snake.speed * rl.get_frame_time())

    # move body
    def move_part(start_pos: rl.Vector2, end_pos: rl.Vector2) -> rl.Vector2:
        direction = rl.vector2_subtract(end_pos, start_pos)
        if rl.vector2_length(direction) < snake.radius:
            return start_pos
        direction   = rl.vector2_normalize(direction)
        circle_edge = rl.vector2_scale(direction, snake.radius)
        return rl.vector2_subtract(end_pos, circle_edge)

    snake.body[0] = move_part(snake.body[0], snake.head)
    for i in range(1, len(snake.body)):
        snake.body[i] = move_part(snake.body[i], snake.body[i - 1])
    return snake

def main():
    WIN_SCALE  = 100
    WIN_WIDTH  = 16 * WIN_SCALE
    WIN_HEIGHT = 9  * WIN_SCALE
    BG_COLOR   = [25, 32, 36, 255]

    rl.set_config_flags(rl.ConfigFlags.FLAG_WINDOW_RESIZABLE | rl.ConfigFlags.FLAG_MSAA_4X_HINT)
    rl.init_window(WIN_WIDTH, WIN_HEIGHT, "Snake")
    rl.set_target_fps(60)

    snake = Snake(
        color     = rl.Color(217, 133, 32, 255),
        radius    = 35,
        speed     = 500,
        head      = rl.Vector2(rl.get_render_width() / 2, rl.get_render_height() / 2),
        body      = [rl.Vector2(0, 0)] * 50,
    )

    camera = rl.Camera2D()
    camera.offset = snake.head
    camera.target = rl.Vector2(rl.get_render_width() / 2, rl.get_render_height() / 2)
    camera.rotation = 0.0
    camera.zoom = 1.0


    spacing = 0
    buildings = []
    build_colors = []
    for _ in range(100):
        width = random.randint(50, 200)
        height = random.randint(100, 800)
        x = -6000.0 + spacing
        y = rl.get_render_height() - 130.0 - height

        spacing += width

        buildings.append(rl.Rectangle(x, y, width, height))
        build_colors.append(rl.Color(
            random.randint(200, 240),
            random.randint(200, 240),
            random.randint(200, 250),
            255
        ))

    WORLD_WIDTH = 6000
    WORLD_HEIGHT = 6000
    while not rl.window_should_close():

        m_pos = rl.get_screen_to_world_2d(rl.get_mouse_position(), camera)
        snake = move_snake_to(snake, m_pos)
        # camera.target = (rl.get_render_width() / 2, rl.get_render_height() / 2)
        camera.target = snake.head

        rl.begin_drawing()
        rl.draw_fps(10, 10)
        rl.clear_background(BG_COLOR)

        rl.begin_mode_2d(camera)

        texture = rl.load_texture("background2.jpg")
        for y in range(0, WORLD_HEIGHT, texture.height):
            for x in range(0, WORLD_WIDTH, texture.width):
                rect = rl.Rectangle(x, y, texture.width, texture.height)
                src_rect = rl.Rectangle(0, 0, texture.width, texture.height)
                rl.draw_texture_pro(texture, src_rect, rect, [0, 0], 0, rl.WHITE)

        draw_snake(snake)
        rec = rl.Rectangle(0, 0, WORLD_WIDTH, WORLD_HEIGHT)
        rl.draw_rectangle_lines_ex(rec, 10, rl.RED)
        rl.end_mode_2d()
        rl.end_drawing()


if __name__ == "__main__":
    main()

