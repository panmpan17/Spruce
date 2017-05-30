import pygame

def count_distance(x, y, x2, y2):
    return ((x2 - x) ** 2 + (y2 - y) ** 2) ** 0.5

class ScreenInfo:
    def __init__(self, width, height, block_size):
        self.width = width
        self.height = height
        self.block_size = block_size

        self.width_blocks = int(width / block_size)
        self.height_blocks = int(height / block_size)

    def set_screen_size(self, width, height):
        self.width = width
        self.height = height

        self.width_blocks = int(width / self.block_size)
        self.height_blocks = int(height / self.block_size)

    def set_block_size(self, block_size):
        self.block_size = block_size

        self.width_blocks = int(self.width / block_size)
        self.height_blocks = int(self.height / block_size)

class MyPygameEvent:
	VBUPDATE = pygame.event.Event(32, {}) # "view_box_update"


class Font:
    def __init__(self):
        self.f12 = pygame.font.Font(None, 12)
        self.f16 = pygame.font.Font(None, 16)
        self.f20 = pygame.font.Font(None, 20)
        self.f24 = pygame.font.Font(None, 24)
        self.f28 = pygame.font.Font(None, 28)
        self.f12text = {}
        self.f16text = {}
        self.f20text = {}
        self.f24text = {}
        self.f28text = {}

    def get_12_text(self, text, color):
        try:
            return self.f12text[text][color]
        except:
            try:
                self.f12text[text][color] = self.f12.render(text, 1, color)
            except:
                self.f12text[text] = {}
                self.f12text[text][color] = self.f12.render(text, 1, color)
            return self.f12text[text][color]

    def get_16_text(self, text, color):
        try:
            return self.f16text[text][color]
        except:
            try:
                self.f16text[text][color] = self.f16.render(text, 1, color)
            except:
                self.f16text[text] = {}
                self.f16text[text][color] = self.f16.render(text, 1, color)
            return self.f16text[text][color]

    def get_20_text(self, text, color):
        try:
            return self.f20text[text][color]
        except:
            try:
                self.f20text[text][color] = self.f28.render(text, 1, color)
            except:
                self.f20text[text] = {}
                self.f20text[text][color] = self.f28.render(text, 1, color)
            return self.f20text[text][color]

    def get_24_text(self, text, color):
        try:
            return self.f24text[text][color]
        except:
            try:
                self.f24text[text][color] = self.f28.render(text, 1, color)
            except:
                self.f24text[text] = {}
                self.f24text[text][color] = self.f28.render(text, 1, color)
            return self.f24text[text][color]

    def get_28_text(self, text, color):
        try:
            return self.f28text[text][color]
        except:
            try:
                self.f28text[text][color] = self.f28.render(text, 1, color)
            except:
                self.f28text[text] = {}
                self.f28text[text][color] = self.f28.render(text, 1, color)
            return self.f28text[text][color]
