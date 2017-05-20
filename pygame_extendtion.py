import pygame

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