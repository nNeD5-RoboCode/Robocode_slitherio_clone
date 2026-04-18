#include "raylib.h"
#include "stdlib.h"
#include "math.h"
#include "time.h"

#define FOOD_COUNT 300
#define WORLD_SIZE 2500

typedef struct {
    float x;
    float y;
    float size;
    Color color;
} Food;

typedef struct {
    Food *items;
    int count;
    int capacity;
    Food *dead_remains;
    int dead_count;
    int dead_capacity;
} FoodSpawner;

typedef struct {
    Vector2 *body;
    int body_size;
    int capacity;
    Vector2 head;
    float radius;
    float speed;
    Color color;
} Snake;

void InitFoodSpawner(FoodSpawner *spawner) {
    spawner->capacity = 64;
    spawner->dead_capacity = 64;
    spawner->items = malloc(sizeof(Food) * spawner->capacity);
    spawner->dead_remains = malloc(sizeof(Food) * spawner->dead_capacity);
    spawner->count = 0;
    spawner->dead_count = 0;
}

void FreeFoodSpawner(FoodSpawner *spawner) {
    free(spawner->items);
    free(spawner->dead_remains);
}

void SpawnOne(FoodSpawner *spawner, Rectangle world_rec) {
    if (spawner->count >= spawner->capacity) {
        spawner->capacity *= 2;
        spawner->items = realloc(spawner->items, sizeof(Food) * spawner->capacity);
    }
    Food food;
    food.x = (float)GetRandomValue((int)world_rec.x, (int)(world_rec.x + world_rec.width));
    food.y = (float)GetRandomValue((int)world_rec.y, (int)(world_rec.y + world_rec.height));
    food.size = (float)GetRandomValue(3, 15);
    food.color = (Color){
        GetRandomValue(0, 255),
        GetRandomValue(0, 255),
        GetRandomValue(0, 255),
        255
    };
    spawner->items[spawner->count++] = food;
}

void SpawnFood(FoodSpawner *spawner, Rectangle world_rec, int target_amount) {
    int to_add = target_amount - spawner->count;
    for (int i = 0; i < to_add; i++) {
        SpawnOne(spawner, world_rec);
    }
}

void SpawnFoodOnSnakeBody(Snake *snake, FoodSpawner *spawner) {
    for (int i = 0; i < snake->body_size; i++) {
        if (spawner->dead_count >= spawner->dead_capacity) {
            spawner->dead_capacity *= 2;
            spawner->dead_remains = realloc(spawner->dead_remains, sizeof(Food) * spawner->dead_capacity);
        }
        Food food = {
            .x = (int)snake->body[i].x,
            .y = (int)snake->body[i].y,
            .size = 1,
            .color = snake->color
        };
        spawner->dead_remains[spawner->dead_count++] = food;
    }
}

void DrawFoodSpawner(FoodSpawner *spawner) {
    for (int i = 0; i < spawner->count; i++) {
        DrawCircle((int)spawner->items[i].x, (int)spawner->items[i].y, spawner->items[i].size, spawner->items[i].color);
    }
    for (int i = 0; i < spawner->dead_count; i++) {
        DrawCircle((int)spawner->dead_remains[i].x, (int)spawner->dead_remains[i].y, spawner->dead_remains[i].size, spawner->dead_remains[i].color);
    }
}

void InitSnake(Snake *snake, Vector2 pos, int body_size, float radius, float speed, Color color) {
    snake->capacity = 64;
    snake->body = malloc(sizeof(Vector2) * snake->capacity);
    snake->body_size = body_size;
    snake->radius = radius;
    snake->speed = speed;
    snake->color = color;
    snake->head = pos;
    for (int i = 0; i < body_size; i++) {
        snake->body[i] = pos;
    }
}

void FreeSnake(Snake *snake) {
    free(snake->body);
}

void DrawSnake(Snake *snake) {
    DrawCircleV(snake->head, snake->radius, snake->color);
    for (int i = 0; i < snake->body_size; i++) {
        DrawCircleV(snake->body[i], snake->radius, snake->color);
    }
}

Vector2 MovePart(Vector2 part, Vector2 target, float radius) {
    Vector2 dir = Vector2Subtract(target, part);
    float l = Vector2Length(dir);
    if (l > 0) {
        dir = Vector2Normalize(dir);
    }
    Vector2 radius_vec = Vector2Scale(dir, radius / 4.0f);
    return Vector2Subtract(target, radius_vec);
}

void MoveSnake(Snake *snake, Vector2 target_pos) {
    Vector2 direction = Vector2Subtract(target_pos, snake->head);
    float len = Vector2Length(direction);
    if (len > 0) {
        direction = Vector2Normalize(direction);
    }
    Vector2 step = Vector2Scale(direction, snake->speed * GetFrameTime());
    snake->head = Vector2Add(snake->head, step);

    snake->body[0] = MovePart(snake->body[0], snake->head, snake->radius);
    for (int i = 1; i < snake->body_size; i++) {
        snake->body[i] = MovePart(snake->body[i], snake->body[i-1], snake->radius);
    }
}

void GrowSnake(Snake *snake) {
    if (snake->body_size >= snake->capacity) {
        snake->capacity *= 2;
        snake->body = realloc(snake->body, sizeof(Vector2) * snake->capacity);
    }
    snake->body[snake->body_size++] = snake->body[snake->body_size - 1];
}

bool IsSnakeDead(Snake *snake, Rectangle world_rec) {
    return !CheckCollisionCircleRec(snake->head, snake->radius, world_rec);
}

void SnakeEatFood(Snake *snake, FoodSpawner *spawner) {
    int to_remove[FOOD_COUNT];
    int remove_count = 0;

    for (int i = 0; i < spawner->count; i++) {
        Vector2 food_pos = { spawner->items[i].x, spawner->items[i].y };
        if (CheckCollisionCircles(snake->head, snake->radius, food_pos, spawner->items[i].size)) {
            GrowSnake(snake);
            to_remove[remove_count++] = i;
        }
    }

    for (int i = remove_count - 1; i >= 0; i--) {
        int idx = to_remove[i];
        spawner->items[idx] = spawner->items[--spawner->count];
    }
}

int main(void) {
    const int WIN_WIDTH = 1600;
    const int WIN_HEIGHT = 900;

    Rectangle world_rec = { 0, 0, WORLD_SIZE, WORLD_SIZE };

    Snake snake;
    InitSnake(&snake,
        (Vector2){ GetRandomValue(100, WORLD_SIZE - 100), GetRandomValue(100, WORLD_SIZE - 100) },
        15, 35.0f, 500.0f,
        (Color){ 152, 251, 152, 255 }
    );

    FoodSpawner food_spawner;
    InitFoodSpawner(&food_spawner);

    InitWindow(WIN_WIDTH, WIN_HEIGHT, "Raylib");
    Texture2D bg_tile = LoadTexture("background_tile.jpg");

    Camera2D camera = { 0 };
    camera.offset = (Vector2){ WIN_WIDTH / 2.0f, WIN_HEIGHT / 2.0f };
    camera.target = snake.head;
    camera.rotation = 0;
    camera.zoom = 1;

    SetTargetFPS(60);

    while (!WindowShouldClose()) {
        BeginDrawing();
        ClearBackground((Color){ 25, 32, 36, 255 });

        BeginMode2D(camera);

        for (int y = -WORLD_SIZE; y < WORLD_SIZE * 2; y += bg_tile.height) {
            for (int x = -WORLD_SIZE; x < WORLD_SIZE * 2; x += bg_tile.width) {
                DrawTexture(bg_tile, x, y, WHITE);
            }
        }

        DrawSnake(&snake);
        DrawFoodSpawner(&food_spawner);

        DrawRectangleLinesEx(world_rec, 10, WHITE);

        Vector2 m_pos = GetMousePosition();
        m_pos = GetScreenToWorld2D(m_pos, camera);
        MoveSnake(&snake, m_pos);
        camera.target = snake.head;
        SnakeEatFood(&snake, &food_spawner);

        SpawnFood(&food_spawner, world_rec, FOOD_COUNT);

        if (IsSnakeDead(&snake, world_rec)) {
            SpawnFoodOnSnakeBody(&snake, &food_spawner);
        }

        EndMode2D();
        DrawFPS(10, 10);
        EndDrawing();
    }

    UnloadTexture(bg_tile);
    FreeSnake(&snake);
    FreeFoodSpawner(&food_spawner);
    CloseWindow();

    return 0;
}