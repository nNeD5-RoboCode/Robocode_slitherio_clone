#!/usr/bin/env python

import pyray as rl


class Snake:
    def __init__(self, pos: rl.Vector2, body_size: int, radius: int, speed: int, color: rl.Color):
        self.radius = radius
        self.speed = speed
        self.color = color

        self.body = [pos] * body_size
        self.head = pos

    def draw(self):
        rl.draw_circle_v(self.head, self.radius, self.color)
        for part in self.body:
            rl.draw_circle_v(part, self.radius, self.color)

    # TODO: m_pos should be argument
    def follow_cursor(self):
        m_pos          = rl.get_mouse_position()
        direction      = rl.vector2_subtract(m_pos, self.head)
        direction_norm = rl.vector2_normalize(direction)
        step           = rl.vector2_scale(direction_norm, self.speed * rl.get_frame_time())
        self.head      = rl.vector2_add(self.head, step)

        def move_part(part: rl.Vector2, target: rl.Vector2) -> rl.Vector2:
            direction      = rl.vector2_subtract(target, part)
            direction_norm = rl.vector2_normalize(direction)
            radius_vector  = rl.vector2_scale(direction_norm, self.radius)
            circle_edge    = rl.vector2_subtract(target, radius_vector)
            return circle_edge

        self.body[0] = move_part(self.body[0], self.head)
        for i in range(1, len(self.body)):
            self.body[i] = move_part(self.body[i], self.body[i - 1])


def main():
    snake = Snake(
        pos=rl.Vector2(100, 100),
        body_size=15,
        radius=35,
        speed=500,
        color=rl.Color(152, 251, 152, 255)
    )
    rl.set_config_flags(rl.ConfigFlags.FLAG_WINDOW_RESIZABLE)
    WIN_SCALE  = 100
    WIN_WIDTH  = 16 * WIN_SCALE
    WIN_HEIGHT = 9  * WIN_SCALE
    rl.init_window(WIN_WIDTH, WIN_HEIGHT, "Raylib")

    BG_TILE = rl.load_texture("background_tile.png")
    camera = rl.Camera2D()
    camera.offset   = (WIN_WIDTH / 2, WIN_HEIGHT / 2)
    camera.target   = snake.head
    camera.rotation = 0
    camera.zoom     = 1

    rl.set_target_fps(60)
    while not rl.window_should_close():
        rl.begin_drawing()
        rl.begin_mode_2d(camera)

        rl.clear_background([25, 32, 36, 255])
        rl.draw_fps(10, 10)


        rl.draw_texture(BG_TILE, 0, 0, rl.WHITE)
        snake.draw()

        snake.follow_cursor()

        rl.end_mode_2d()
        rl.end_drawing()

    rl.close_window()


if __name__ == "__main__":
    main()
