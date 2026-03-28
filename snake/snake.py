#!/usr/bin/env python

from random import randint

import pyray as rl

class Food:
    def __init__(self):
        self.food_positions: list[rl.Vector2] = []

    def spawn(self, world_rec: rl.Rectangle):
        self.food_positions.append(rl.Vector2(
            randint(int(world_rec.x), int(world_rec.x + world_rec.width)),
            randint(int(world_rec.y), int(world_rec.y + world_rec.height))
        ))

    def draw(self):
        # TODO: shader for gloving
        for pos in self.food_positions:
            rl.draw_circle_v(pos, randint(3, 10), rl.WHITE)


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

    def move_to(self, target_pos: rl.Vector2):
        direction      = rl.vector2_subtract(target_pos, self.head)
        direction_norm = rl.vector2_normalize(direction)
        step           = rl.vector2_scale(direction_norm, self.speed * rl.get_frame_time())
        self.head      = rl.vector2_add(self.head, step)

        def move_part(part: rl.Vector2, target: rl.Vector2) -> rl.Vector2:
            direction      = rl.vector2_subtract(target, part)
            direction_norm = rl.vector2_normalize(direction)
            radius_vector  = rl.vector2_scale(direction_norm, self.radius/4)
            circle_edge    = rl.vector2_subtract(target, radius_vector)
            return circle_edge

        self.body[0] = move_part(self.body[0], self.head)
        for i in range(1, len(self.body)):
            self.body[i] = move_part(self.body[i], self.body[i - 1])


def main():
    rl.set_config_flags(rl.ConfigFlags.FLAG_WINDOW_RESIZABLE)
    WIN_SCALE  = 100
    WIN_WIDTH  = 16 * WIN_SCALE
    WIN_HEIGHT = 9  * WIN_SCALE
    WORLD_SIZE = 2500
    WORLD_REC = rl.Rectangle(0, 0, WORLD_SIZE, WORLD_SIZE)
    snake = Snake(
        pos=rl.Vector2(randint(100, WORLD_SIZE - 100), randint(100, WORLD_SIZE - 100)),
        body_size=15,
        radius=35,
        speed=500,
        color=rl.Color(152, 251, 152, 255)
    )
    rl.init_window(WIN_WIDTH, WIN_HEIGHT, "Raylib")

    BG_TILE = rl.load_texture("snake/background_tile.png")
    camera = rl.Camera2D()
    camera.offset   = (WIN_WIDTH / 2, WIN_HEIGHT / 2)
    camera.target   = snake.head
    camera.rotation = 0
    camera.zoom     = 1

    rl.set_target_fps(60)
    while not rl.window_should_close():
        rl.begin_drawing()
        rl.clear_background([25, 32, 36, 255])
        rl.begin_mode_2d(camera)

        for y in range(-WORLD_SIZE, WORLD_SIZE * 2, BG_TILE.height):
            for x in range(-WORLD_SIZE, WORLD_SIZE * 2, BG_TILE.width):
                rl.draw_texture(BG_TILE, x, y, rl.WHITE)
        snake.draw()

        rl.draw_rectangle_lines_ex(WORLD_REC, 10, rl.WHITE)

        m_pos = rl.get_mouse_position()
        m_pos = rl.get_screen_to_world_2d(m_pos, camera)
        snake.move_to(m_pos)
        camera.target = snake.head

        if not rl.check_collision_point_rec(snake.head, WORLD_REC):
            rl.close_window()

        rl.end_mode_2d()
        rl.draw_fps(10, 10)
        rl.end_drawing()

    rl.close_window()


if __name__ == "__main__":
    main()
