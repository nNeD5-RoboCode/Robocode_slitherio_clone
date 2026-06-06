#!/usr/bin/env -S uv run --script
# /// script
# dependencies = []
# ///

from network import MessageSnake, snake_to_msg, msg_to_snake
from random import randint
import pyray as rl


MAX_SNAKE_SIZE = 500
MAX_MSG_SIZE   = 4 + 5 + MAX_SNAKE_SIZE * 15

WIN_SCALE  = 100
WIN_WIDTH  = 16 * WIN_SCALE
WIN_HEIGHT = 9  * WIN_SCALE
WORLD_SIZE = 2500
WORLD_REC  = rl.Rectangle(0, 0, WORLD_SIZE, WORLD_SIZE)

camera          = rl.Camera2D()
camera.offset   = rl.Vector2(WIN_WIDTH / 2, WIN_HEIGHT / 2)
camera.rotation = 0
camera.zoom     = 1


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

    def grow(self, food: Food):
        # TODO: add new circle only after some amount of food
        # TODO: slow down grows accroding to snake size
        # TODO: change camera zoom on discrete size change
        new_cicrles_number = 0
        if food.size > 3 and food.size <= 7:
            new_cicrles_number = 1
        elif food.size > 7 and food.size <= 11:
            new_cicrles_number = 2
        elif food.size > 11 and food.size <= 15:
            new_cicrles_number = 3

        if len(self.body) + new_cicrles_number < MAX_SNAKE_SIZE:
            for _ in range(0, new_cicrles_number):
                self.body.append(self.body[-1])
                self.radius += 0.07
                camera.zoom -= 0.001
                if camera.zoom < 0.8:
                    camera.zoom = 0.8


    def is_snake_dead(self, world_rec: rl.Rectangle) -> bool:
        if not rl.check_collision_circle_rec(self.head, self.radius, world_rec):
            return True
        return False

    def reset(self, world_rec: rl.Rectangle):
        self.head.x = randint(100, int(world_rec.width)  - 100)
        self.head.y = randint(100, int(world_rec.height) - 100)
        self.radius = 35
        self.body   = [rl.vector2_zero()] * 15




def snake_eat_food(snake: Snake, food_spawner: FoodSpawner):
    food_id_to_remove = []
    for food_id, food in enumerate(food_spawner.food_items):
        food_pos = rl.Vector2(food.x, food.y)
        if rl.check_collision_circles(snake.head, snake.radius, food_pos, food.size):
            snake.grow(food)
            food_id_to_remove.append(food_id)

    for i in food_id_to_remove:
        if i < len(food_spawner.food_items):
            food_spawner.food_items.pop(i)


def update_snakes(snakes: dict, msg: str):
    # "snake@snake@snake"
    # "snake=0:35.35:1 0, 200 100, -20, 60"
    # "0:35.35:1 0, 200 100, -20, 60@0:35.35:1 0, 200 100, -20, 60"
    # "0:35.35:1 0, 200 100, -20, 60@0:35.35:@"
    print(f"update_snakes: {msg}")
    snakes_msgs = msg.split("@")
    if len(msg) == 0:
        return

    for snake_msg in snakes_msgs:
        if not snake_msg:
            continue
        parts = snake_msg.split(":")
        if parts != 3:
            print("I'm here")
            continue
        id_, radius, body = snake_msg.split(":")
        body = body.split(",")
        if not body[0]:
            continue
        head = body[0]
        head = head.split()
        head = rl.Vector2(float(head[0]), float(head[1]))
        body = body[1:]
        for i in range(len(body)):
            body[i] = body[i].split()
            body[i] = rl.Vector2(float(body[i][0]), float(body[i][1]))
        id_ = int(id_)
        radius = float(radius)
        if id_ not in snakes:
            snakes[id_] = Snake(
                pos=rl.vector2_zero(),
                body_size=1,
                radius=1,
                speed=500,
                color=rl.Color(randint(0, 255), randint(0, 255), randint(0, 255), 255)
            )
        snakes[id_].radius = radius
        snakes[id_].head   = head
        snakes[id_].body   = body


def game(client_id: int=0, client=None):
    snake = Snake(
        pos=rl.Vector2(randint(100, WORLD_SIZE - 100), randint(100, WORLD_SIZE - 100)),
        body_size=35,
        radius=35,
        speed=500,
        color=rl.Color(152, 251, 152, 255)
    )
    food_spawner = FoodSpawner(100)
    snakes = {}

    BG_TILE = rl.load_texture("background_tile.jpg")
    bg_texure = rl.load_render_texture(WORLD_SIZE * 3, WORLD_SIZE * 3)

    bg_src_rec = rl.Rectangle(0, 0, WORLD_SIZE*3, WORLD_SIZE*3)
    bg_dst_rec = rl.Rectangle(-WORLD_SIZE, -WORLD_SIZE, WORLD_SIZE*3, WORLD_SIZE*3)
    rl.begin_texture_mode(bg_texure)
    for y in range(0, WORLD_SIZE * 3, BG_TILE.height):
        for x in range(0, WORLD_SIZE * 3, BG_TILE.width):
            rl.draw_texture(BG_TILE, x, y, rl.WHITE)
    rl.end_texture_mode()

    rl.set_target_fps(60)
    while not rl.window_should_close():
        rl.begin_drawing()
        rl.clear_background([25, 32, 36, 255])
        rl.begin_mode_2d(camera)

        rl.draw_texture_pro(bg_texure.texture, bg_src_rec, bg_dst_rec, (0, 0),  0, rl.WHITE)

        food_spawner.draw()
        snake.draw()

        rl.draw_rectangle_lines_ex(WORLD_REC, 10, rl.WHITE)

        m_pos = rl.get_mouse_position()
        m_pos = rl.get_screen_to_world_2d(m_pos, camera)
        snake.move_to(m_pos)
        camera.target = snake.head
        snake_eat_food(snake, food_spawner)

        food_spawner.spawn(WORLD_REC)

        if snake.is_snake_dead(WORLD_REC):
            food_spawner.spawn_food_on_snake_body(snake)
            snake.reset(WORLD_REC)

        for cid, client_snake in snakes.items():
            if client_id == cid:
                continue
            client_snake.draw()
            # print("Drawing other client snake ...")
            # print(f"{client_snake.head.x = } {client_snake.head.y = }")
            # print()

        rl.end_mode_2d()
        rl.draw_fps(10, 10)
        rl.end_drawing()

        if client:
            msg_snake = MessageSnake()
            msg_snake.radius = snake.radius
            msg_snake.body_coords = [snake.head] + snake.body
            msg = snake_to_msg(msg_snake)
            client.send(msg)

            msg = client.receive()
            if msg:
                # print(f"game.client.receive: {msg}")
                update_snakes(snakes, msg)

    rl.close_window()


if __name__ == "__main__":
    rl.set_config_flags(rl.ConfigFlags.FLAG_WINDOW_RESIZABLE)
    rl.init_window(WIN_WIDTH, WIN_HEIGHT, "Raylib")
    game()
