#!/usr/bin/env python

import pyray as pr

pr.set_config_flags(pr.ConfigFlags.FLAG_WINDOW_RESIZABLE)
WIN_SCALE  = 100
WIN_WIDTH  = 16 * WIN_SCALE
WIN_HEIGHT = 9  * WIN_SCALE
pr.init_window(WIN_WIDTH, WIN_HEIGHT, "Raylib")
pr.set_target_fps(60)
while not pr.window_should_close():
    dt = pr.get_frame_time()
    pr.begin_drawing()
    pr.draw_fps(10, 10)
    pr.clear_background([25, 32, 36, 255])
    pr.draw_circle(100, 100, 75, [217, 133, 32, 255])
    pr.end_drawing()
pr.close_window()
