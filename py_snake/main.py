#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["raylib", "numpy"]
# ///


from dataclasses import dataclass
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
        head      = rl.Vector2(100, 100),
        body      = [rl.Vector2(0, 0)] * 10,
    )

    while not rl.window_should_close():
        rl.begin_drawing()
        rl.draw_fps(10, 10)
        rl.clear_background(BG_COLOR)
        draw_snake(snake)
        rl.end_drawing()

        snake = move_snake_to(snake, rl.get_mouse_position())


if __name__ == "__main__":
    main()

