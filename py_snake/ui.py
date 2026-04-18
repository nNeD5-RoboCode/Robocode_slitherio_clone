import pyray as rl

class Button:
    def __init__(self, rect: rl.Rectangle, texture: rl.Texture2D):
        self.rect       = rect
        self.texture    = texture
        self.is_hovered = False
        self.is_pressed = False

    def draw(self):
        self._update()
        src_rect = rl.Rectangle(0, 0, self.texture.width, self.texture.height)
        color = rl.WHITE
        if self.is_hovered: color = rl.LIGHTGRAY
        if self.is_pressed: color = rl.GRAY
        rl.draw_texture_pro(self.texture, src_rect, self.rect, [0, 0], 0, color)

    def _update(self):
        if rl.check_collision_point_rec(rl.get_mouse_position(), self.rect):
            self.is_hovered = True
            if rl.is_mouse_button_down(rl.MOUSE_LEFT_BUTTON):
                self.is_pressed = True
            else:
                self.is_pressed = False
        else:
            self.is_hovered = False
            self.is_pressed = False

    def is_clicked(self) -> bool:
        if rl.is_mouse_button_released(rl.MOUSE_LEFT_BUTTON) and self.is_hovered:
            return True
        return False


class InputBox:
    def __init__(self, rect: rl.Rectangle):
        self.rect = rect
        self.text = ""
        self.is_hovered = False
        self.is_focused = False
        self.max_chars = 15

    def draw(self):
        self._update()
        rl.draw_rectangle_rounded(self.rect, 0.2, 10, rl.DARKGRAY)
        border_color = rl.GREEN if self.is_focused else rl.LIGHTGRAY
        rl.draw_rectangle_rounded_lines_ex(self.rect, 0.2, 10, 5, border_color)
        font_size = 30
        text_x = int(self.rect.x + 10)
        text_y = int(self.rect.y + (self.rect.height - font_size) / 2)
        rl.draw_text(self.text, text_x, text_y, font_size, rl.WHITE)
        if self.is_focused:
            if (int(rl.get_time() * 2) % 2) == 0:
                text_width = rl.measure_text(self.text, font_size)
                rl.draw_text("|", text_x + text_width + 2, text_y, font_size, rl.WHITE)


    def is_accepted(self) -> bool:
        return self.is_focused and rl.is_key_released(rl.KEY_ENTER)

    def _update(self):
        if rl.check_collision_point_rec(rl.get_mouse_position(), self.rect):
            self.is_hovered = True
            rl.set_mouse_cursor(rl.MOUSE_CURSOR_IBEAM)
        else:
            self.is_hovered = False
            rl.set_mouse_cursor(rl.MOUSE_CURSOR_DEFAULT)

        if rl.is_mouse_button_pressed(rl.MOUSE_LEFT_BUTTON):
            self.is_focused = self.is_hovered

        if self.is_focused:
            key = rl.get_char_pressed()
            while key > 0:
                if (key >= 32) and (key <= 125) and (len(self.text) < self.max_chars):
                    self.text += chr(key)
                key = rl.get_char_pressed()

            if rl.is_key_pressed(rl.KEY_BACKSPACE):
                if len(self.text) > 0:
                    self.text = self.text[:-1]
