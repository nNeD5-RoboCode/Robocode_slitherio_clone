#include <raylib.h>
#include <raymath.h>
#include <rlgl.h>
#include <math.h>

void DrawTexturedRing(Texture2D tex, Vector2 center,
                      float innerR, float outerR,
                      int segments)
{
    float radius = (innerR + outerR) * 0.5f;
    float thickness = (outerR - innerR);

    for (int i = 0; i < segments; i++)
    {
        float t1 = (float)i / segments;
        float t2 = (float)(i + 1) / segments;

        float a1 = t1 * 2*PI;
        float a2 = t2 * 2*PI;

        Vector2 p1 = {
            center.x + cosf(a1) * radius,
            center.y + sinf(a1) * radius
        };

        Vector2 p2 = {
            center.x + cosf(a2) * radius,
            center.y + sinf(a2) * radius
        };

        float len = Vector2Distance(p1, p2);
        float angle = atan2f(p2.y - p1.y, p2.x - p1.x) * RAD2DEG;

        Rectangle src = {
            t1 * tex.width, 0,
            (t2 - t1) * tex.width,
            tex.height
        };

        Rectangle dst = {
            p1.x, p1.y,
            len, thickness
        };

        Vector2 origin = {0, thickness/2};

        DrawTexturePro(tex, src, dst, origin, angle, WHITE);
    }
}

int main(void)
{
    InitWindow(800, 600, "Donut");

    // Image img = GenImageChecked(256, 64, 16, 16, DARKGREEN, GREEN);
    // Texture2D tex = LoadTextureFromImage(img);
    // UnloadImage(img);
 
    Texture2D tex = LoadTexture("texture.png");

    SetTextureWrap(tex, TEXTURE_WRAP_REPEAT);

    Vector2 center = {400, 300};

    while (!WindowShouldClose())
    {
        BeginDrawing();
        ClearBackground(RAYWHITE);

        DrawTexturedRing(tex, center, 80, 150, 100);

        DrawCircle(400, 300, 5, RED); // debug center

        EndDrawing();
    }

    UnloadTexture(tex);
    CloseWindow();
}
