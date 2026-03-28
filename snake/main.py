#!/usr/bin/env python
from this import s
from typing import final

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
        for seg in self.body:
            rl.draw_circle_v(seg, self.radius, self.color)


    def follow_cursor(self):
        m_pos = rl.get_mouse_position()
        direction = rl.vector2_subtract(m_pos, self.head)
        direction_norm = rl.vector2_normalize(direction)
        step = rl.vector2_scale(direction_norm, self.speed * rl.get_frame_time())
        self.head = rl.vector2_add(self.head, step)

        def move_part(follower: rl.Vector2, followed: rl.Vector2) -> rl.Vector2:
            direction = rl.vector2_subtract(followed, follower)
            direction_norm = rl.vector2_normalize(direction)
            radius_vector = rl.vector2_scale(direction_norm, self.radius)
            final_pos = rl.vector2_subtract(followed, radius_vector)
            return final_pos

        self.body[0] = move_part(self.body[0], self.head)
        for i in range(1, len(self.body)):
            self.body[i] = move_part(self.body[i], self.body[i - 1])


def main():
    snake = Snake(
        pos=rl.Vector2(100, 100),
        body_size=5,
        radius=35,
        speed=500,
        color=rl.Color(152, 251, 152, 255)
    )

    rl.set_config_flags(rl.ConfigFlags.FLAG_WINDOW_RESIZABLE)
    WIN_SCALE  = 100
    WIN_WIDTH  = 16 * WIN_SCALE
    WIN_HEIGHT = 9  * WIN_SCALE
    rl.init_window(WIN_WIDTH, WIN_HEIGHT, "Raylib")
    rl.set_target_fps(60)
    while not rl.window_should_close():
        rl.begin_drawing()
        rl.draw_fps(10, 10)
        rl.clear_background([25, 32, 36, 255])
        snake.draw()
        rl.end_drawing()

        snake.follow_cursor()

    rl.close_window()


if __name__ == "__main__":
    main()
