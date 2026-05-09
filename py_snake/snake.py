#!/usr/bin/env python

from random import randint
from dataclasses import dataclass

import pyray as rl


TEXTURES = {}

@dataclass
class Food:
    pos:   rl.Vector2
    size:  int
    color: rl.Color


@dataclass
class FoodSpawner:
    max_food_amount: int
    food_list: list[Food] = []
    dead_snake_remains: list[Food] = []


@dataclass
class Snake:
    radius: int
    speed:  float
    color:  rl.Color

    body:   list[rl.Vector2]
    head:   rl.Vector2

@dataclass
class GameState:
    snake:        Snake
    food_spawner: FoodSpawner
    world_rec:    rl.Rectangle
    camera:       rl.Camera2D


def snake_draw(snake: Snake):
    rl.draw_circle_v(snake.head, snake.radius, snake.color)
    for part in snake.body:
        rl.draw_circle_v(part, snake.radius, snake.color)


def snake_move(game_state: GameState):
    snake = game_state.snake

    m_pos = rl.get_mouse_position()
    m_pos = rl.get_screen_to_world_2d(m_pos, game_state.camera)

    direction      = rl.vector2_subtract(m_pos, snake.head)
    direction_norm = rl.vector2_normalize(direction)
    step           = rl.vector2_scale(direction_norm, snake.speed * rl.get_frame_time())
    snake.head      = rl.vector2_add(snake.head, step)

    def move_part(part: rl.Vector2, target: rl.Vector2) -> rl.Vector2:
        direction      = rl.vector2_subtract(target, part)
        direction_norm = rl.vector2_normalize(direction)
        radius_vector  = rl.vector2_scale(direction_norm, snake.radius/4)
        circle_edge    = rl.vector2_subtract(target, radius_vector)
        return circle_edge

    snake.body[0] = move_part(snake.body[0], snake.head)
    for i in range(1, len(snake.body)):
        snake.body[i] = move_part(snake.body[i], snake.body[i - 1])



def food_spawn(game_state: GameState):
    world_rec    = game_state.world_rec
    food_spawner = game_state.food_spawner

    n = food_spawner.max_food_amount - len(food_spawner.food_list)
    for _ in range(0, n):
        x = randint(int(world_rec.x), int(world_rec.x + world_rec.width))
        y = randint(int(world_rec.y), int(world_rec.y + world_rec.height))
        pos = rl.Vector2(x, y)
        size = randint(3, 15)
        color = rl.Color(randint(0, 255), randint(0, 255), randint(0, 255), 255)
        food = Food(pos, size, color)
        food_spawner.food_list.append(food)


def food_spawn_on_snake_body(game_state: GameState):
    for snake_part in game_state.snake.body:
        pos = rl.Vector2(snake_part.x, snake_part.y)
        food = Food(pos, randint(3, snake.radius), snake.color)
        game_state.food_spawner.dead_snake_remains.append(food)


def draw(game_state: GameState):
    # TODO: shader for gloving
    for food in game_state.food_spawner.food_list:
        rl.draw_circle_v(food.pos, food.size, food.color)
    for food in game_state.food_spawner.dead_snake_remains:
        rl.draw_circle_v(food.pos, food.size, food.color)


def snake_grow(game_state: GameState, food: Food):
    # TODO: add new circle only after some amount of food
    # TODO: slow down grows accroding to snake size
    # TODO: change camera zoom on discrete
    snake = game_state.snake
    new_cicrles_number = 0
    if food.size > 3 and food.size <= 7:
        new_cicrles_number = 1
    elif food.size > 7 and food.size <= 11:
        new_cicrles_number = 2
    elif food.size > 11 and food.size <= 15:
        new_cicrles_number = 3

    snake = game_state.snake
    for _ in range(0, new_cicrles_number):
        snake.body.append(snake.body[-1])
        snake.radius += 0.05
        game_state.camera.zoom -= 0.001
        if camera.zoom < 0.8:
            camera.zoom = 0.8


def is_snake_dead(game_state: GameState) -> bool:
    if not rl.check_collision_circle_rec(game_state.snake.head, game_state.snake.radius, game_state.world_rec):
        return True
    return False


def snake_eat_food(game_state: GameState):
    food_spawner = game_state.food_spawner
    snake        = game_state.snake

    food_id_to_remove = []
    for food_id, food in enumerate(food_spawner.food_list):
        if rl.check_collision_circles(snake.head, snake.radius, food.pos, food.size):
            snake_grow(game_state, food)
            food_id_to_remove.append(food_id)

    for i in food_id_to_remove:
        if i < (len(food_spawner.food_list)):
            food_spawner.food_list.pop(i)



def game_update(game_state: GameState):
    rl.begin_mode_2d(camera)

    snake_move(game_state)
    game_state.camera.target = snake.head
    game_state.camera.offset = rl.Vector2(rl.get_render_width() / 2, rl.get_render_height() / 2)

    snake_eat_food(game_state)

    food_spawn(game_state)

    if is_snake_dead(game_state):
        food_spawn_on_snake_body(game_state)

    rl.end_mode_2d()


def game_draw(game_state: GameState):
    rl.begin_drawing()
    rl.begin_mode_2d(camera)
    rl.clear_background([25, 32, 36, 255])

    for y in range(-game_state.WORLD_REC, game_state.WORLD_SIZE * 2, TEXTURES["bg_tile"].height):
        for x in range(-game_state.WORLD_SIZE, -game_state.WORLD_SIZE * 2, TEXTURES["bg_tile"].width):
            rl.draw_texture(BG_TILE, x, y, rl.WHITE)

    snake.draw()

    food_spawner.draw()

    rl.draw_rectangle_lines_ex(game_state.world_rec, 10, rl.WHITE)

    rl.draw_fps(10, 10)

    rl.end_drawing()
    rl.end_mode_2d()


if __name__ == "__main__":
    rl.set_config_flags(rl.ConfigFlags.FLAG_WINDOW_RESIZABLE)
    rl.init_window(WIN_WIDTH, WIN_HEIGHT, "Raylib")
    rl.set_target_fps(60)

    snake = Snake(
        radius = 5,
        speed  = 300,
        color  = rl.Color(169, 50, 50, 255),

        body   = [rl.vector_zero()] * 5,
        head   =  rl.vector_zero(),
    )
    camera = rl.Camera2D()
    camera.offset   = rl.Vector2(WIN_WIDTH / 2, WIN_HEIGHT / 2)
    camera.target   = snake.head
    camera.rotation = 0
    camera.zoom     = 1
    game_state = GameState(
        snake        = snake,
        food_spawner = FoodSpawner(300),
        world_rec    = rl.Rectangle(0, 0, 2500, 2500),
        camera       = camera,
    )
    TEXTURES["bg_tile"] = rl.load_texture("background_tile.jpg")

    while not rl.window_should_close():
        game_update()


    rl.close_window()
