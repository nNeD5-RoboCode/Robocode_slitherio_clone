#!/usr/bin/env -S uv run --script
# /// script
# dependencies = []
# ///


from random import randint
import cProfile

import pyray as rl

class Food:
    def __init__(self, x: int, y: int, size: int, color: rl.Color):
        self.x = x
        self.y = y
        self.size = size
        self.color = color

    def draw(self):
        rl.draw_circle(self.x, self.y, self.size, self.color)

class FoodSpawner:
    def __init__(self, food_amount: int):
        self.food_items: list[Food] = []
        self.food_amount = food_amount
        self.dead_snake_remains: list[Food] = []

    def spawn_one(self, world_rec: rl.Rectangle):
        x = randint(int(world_rec.x), int(world_rec.x + world_rec.width))
        y = randint(int(world_rec.y), int(world_rec.y + world_rec.height))
        size = randint(3, 15)
        color = rl.Color(randint(0, 255), randint(0, 255), randint(0, 255), 255)
        food = Food(x, y, size, color)
        self.food_items.append(food)

    def spawn(self, world_rec: rl.Rectangle):
        current_food_amount = len(self.food_items)
        amount_to_add = self.food_amount - current_food_amount
        for _ in range(0, amount_to_add):
            self.spawn_one(world_rec)

    def spawn_food_on_snake_body(self, snake):
        for snake_part in snake.body:
            food = Food(int(snake_part.x), int(snake_part.y), 1, snake.color)
            self.dead_snake_remains.append(food)



    def draw(self):
        # TODO: shader for gloving
        for food in self.food_items:
            food.draw()
        for food in self.dead_snake_remains:
            food.draw()



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

    def grow(self):
        # TODO: grow should depends on food size
        # collided food as parameter?
        self.body.append(self.body[-1])

    def is_snake_dead(self, world_rec: rl.Rectangle) -> bool:
        if not rl.check_collision_circle_rec(self.head, self.radius, world_rec):
            return True
        return False


def snake_eat_food(snake: Snake, food_spawner: FoodSpawner):
    # TODO: strange bug: try to pop not existing food
    food_id_to_remove = []
    for food_id, food in enumerate(food_spawner.food_items):
        food_pos = rl.Vector2(food.x, food.y)
        if rl.check_collision_circles(snake.head, snake.radius, food_pos, food.size):
            snake.grow()
            food_id_to_remove.append(food_id)

    for i in food_id_to_remove:
        food_spawner.food_items.pop(i)



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
    food_spawner = FoodSpawner(300)
    rl.init_window(WIN_WIDTH, WIN_HEIGHT, "Raylib")

    BG_TILE = rl.load_texture("background_tile.jpg")
    camera = rl.Camera2D()
    camera.offset   = rl.Vector2(WIN_WIDTH / 2, WIN_HEIGHT / 2)
    camera.target   = snake.head
    camera.rotation = 0
    camera.zoom     = 1

    render_texture = rl.load_render_texture(WIN_WIDTH, WIN_HEIGHjt)

    # rl.set_target_fps(60)
    while not rl.window_should_close():
        rl.begin_mode_2d(camera)

        # DRAWING
        rl.begin_texture_mode(render_texture)
        for y in range(-WORLD_SIZE, WORLD_SIZE * 2, BG_TILE.height):
            for x in range(-WORLD_SIZE, WORLD_SIZE * 2, BG_TILE.width):
                rl.draw_texture(BG_TILE, x, y, rl.WHITE)

        snake.draw()
        food_spawner.draw()
        rl.draw_rectangle_lines_ex(WORLD_REC, 10, rl.WHITE)
        rl.end_texture_mode()

        # INPUT
        m_pos = rl.get_mouse_position()
        m_pos = rl.get_screen_to_world_2d(m_pos, camera)
        snake.move_to(m_pos)
        camera.target = snake.head
        snake_eat_food(snake, food_spawner)

        food_spawner.spawn(WORLD_REC)

        if snake.is_snake_dead(WORLD_REC):
            food_spawner.spawn_food_on_snake_body(snake)

        rl.end_mode_2d()


        rl.begin_drawing()
        rl.clear_background([25, 32, 36, 255])
        rl.draw_texture(render_texture, 0, 0)
        rl.draw_fps(10, 10)
        rl.end_drawing()

    rl.close_window()


if __name__ == "__main__":
    # cProfile.run("main()", "profiler_output")
    main()
