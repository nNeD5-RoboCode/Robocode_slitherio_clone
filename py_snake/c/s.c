#include "raylib.h"
#include "raymath.h"
#include "rlgl.h"
#include <math.h>

#define MAX_POINTS 200
#define RESOLUTION 10
#define WIDTH 15.0f

// ---------------- CATMULL ROM ----------------
Vector2 CatmullRom(Vector2 p0, Vector2 p1, Vector2 p2, Vector2 p3, float t)
{
    float t2 = t*t;
    float t3 = t2*t;

    Vector2 r;

    r.x = 0.5f * (
        (2*p1.x) +
        (-p0.x + p2.x)*t +
        (2*p0.x - 5*p1.x + 4*p2.x - p3.x)*t2 +
        (-p0.x + 3*p1.x - 3*p2.x + p3.x)*t3
    );

    r.y = 0.5f * (
        (2*p1.y) +
        (-p0.y + p2.y)*t +
        (2*p0.y - 5*p1.y + 4*p2.y - p3.y)*t2 +
        (-p0.y + 3*p1.y - 3*p2.y + p3.y)*t3
    );

    return r;
}

// ---------------- NORMALIZE ----------------
Vector2 NormalizeSafe(Vector2 v)
{
    float len = sqrtf(v.x*v.x + v.y*v.y);
    if (len == 0) return (Vector2){1,0};
    return (Vector2){ v.x/len, v.y/len };
}

// ---------------- MAIN ----------------
int main(void)
{
    InitWindow(1000, 700, "Smooth Snake - Raylib");

    Texture2D bodyTex = LoadTexture("body.png");
    Texture2D headTex = LoadTexture("head.png");

    Vector2 points[MAX_POINTS];
    int pointCount = 0;

    Vector2 smooth[MAX_POINTS * RESOLUTION];
    int smoothCount = 0;

    SetTargetFPS(60);

    while (!WindowShouldClose())
    {
        Vector2 mouse = GetMousePosition();

        // ---------------- UPDATE POINTS ----------------
        if (pointCount == 0)
        {
            points[pointCount++] = mouse;
        }
        else
        {
            Vector2 last = points[pointCount - 1];

            if (Vector2Distance(last, mouse) > 5.0f)
            {
                if (pointCount < MAX_POINTS)
                {
                    // shift-like behavior (snake grows forward)
                    for (int i = pointCount; i > 0; i--)
                        points[i] = points[i-1];

                    points[0] = mouse;
                    pointCount++;
                }
                else
                {
                    for (int i = pointCount-1; i > 0; i--)
                        points[i] = points[i-1];

                    points[0] = mouse;
                }
            }
        }

        // ---------------- SMOOTH PATH ----------------
        smoothCount = 0;

        if (pointCount > 3)
        {
            for (int i = 0; i < pointCount - 3; i++)
            {
                for (int j = 0; j < RESOLUTION; j++)
                {
                    float t = (float)j / RESOLUTION;
                    smooth[smoothCount++] =
                        CatmullRom(points[i], points[i+1], points[i+2], points[i+3], t);
                }
            }
        }

        BeginDrawing();
        ClearBackground((Color){20, 20, 30, 255});

        // =========================================================
        // DRAW BODY (TEXTURED RIBBON)
        // =========================================================
        rlSetTexture(bodyTex.id);

        rlBegin(RL_QUADS);

        float uvScroll = 0.0f;

        for (int i = 1; i < smoothCount - 1; i++)
        {
            Vector2 p0 = smooth[i - 1];
            Vector2 p1 = smooth[i];
            Vector2 p2 = smooth[i + 1];

            Vector2 dir = NormalizeSafe(Vector2Subtract(p2, p0));
            Vector2 normal = (Vector2){ -dir.y, dir.x };

            Vector2 offset = Vector2Scale(normal, WIDTH);

            Vector2 left  = Vector2Add(p1, offset);
            Vector2 right = Vector2Subtract(p1, offset);

            float v = (float)i / smoothCount;

            rlTexCoord2f(0, v + uvScroll);
            rlVertex2f(left.x, left.y);

            rlTexCoord2f(1, v + uvScroll);
            rlVertex2f(right.x, right.y);
        }

        rlEnd();
        rlSetTexture(0);

        // =========================================================
        // DRAW HEAD
        // =========================================================
        if (smoothCount > 2)
        {
            Vector2 head = smooth[smoothCount - 1];
            Vector2 prev = smooth[smoothCount - 2];

            Vector2 dir = NormalizeSafe(Vector2Subtract(head, prev));
            float angle = atan2f(dir.y, dir.x) * RAD2DEG;

            Rectangle src = { 0, 0, (float)headTex.width, (float)headTex.height };

            Rectangle dst = {
                head.x,
                head.y,
                headTex.width,
                headTex.height
            };

            Vector2 origin = {
                headTex.width * 0.5f,
                headTex.height * 0.5f
            };

            DrawTexturePro(headTex, src, dst, origin, angle, WHITE);
        }

        // Debug
        DrawText("Move mouse to control snake", 10, 10, 20, RAYWHITE);

        EndDrawing();
    }

    UnloadTexture(bodyTex);
    UnloadTexture(headTex);
    CloseWindow();

    return 0;
}
