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
        f12 = pygame.font.SysFont(None, 12)
        f16 = pygame.font.SysFont(None, 16)
        f20 = pygame.font.SysFont(None, 20)
        f24 = pygame.font.SysFont(None, 24)