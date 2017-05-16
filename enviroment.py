import pygame
import os
from color import clr

GRASS = '0'
ROCK = '1'

GROUND = 0
UNDERGROUND = 1

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

class Layer:
    def __init__(self, type_, map_, width, height, draw_index, screen):
        self.type = type_
        self.map = map_
        self.width = width
        self.height = height
        self.draw_index = draw_index

        self.screen = screen

        if type_ == GROUND:
            self.image_source = pygame.image.load("texture/grass.png")
            self.texture = "grass"

    def change_screen_size(self):
        width, height = self.screen.width, self.screen.height
        block_size = self.screen.block_size
        filename = f"/texture/extend/{width}x{height}-{block_size}-{self.texture}.png"
        filename = os.getcwd() + filename
        try:
            self.bg = pygame.image.load(filename)
        except:
            # there's no extend background so make one this file will delete at the end
            image_w, image_h = self.image_source.get_size()

            # set up a pygame surface then fill image in it
            make_bg_surface = pygame.display.set_mode((width, height))
            resized_img = pygame.transform.scale(self.image_source,
                (block_size, block_size))

            for w in range(0, width, block_size):
                for h in range(0, height, block_size):
                    make_bg_surface.blit(resized_img, (w, h))
            pygame.display.flip()

            # save it and load it, so next time can use it
            pygame.image.save(make_bg_surface, filename)
            self.bg = pygame.image.load(filename)
            del make_bg_surface

    def render(self, surface, viewX, viewY):
        if self.type == GROUND:
            surface.blit(self.bg, (0, 0))

        blk_sz = self.screen.block_size
        for col in self.draw_index:
            # check col is in the range need to display
            if col >= viewY and col - viewY < self.screen.height_blocks:
                for row in self.draw_index[col]:
                    # check row is in the range need to display
                    if row >= viewX and row - viewX < self.screen.width_blocks:
                        y = (col - viewY) * blk_sz
                        x = (row - viewX) * blk_sz

                        cell = self.draw_index[col][row]

                        # draw block texture
                        if cell == ROCK:
                            pygame.draw.rect(surface, clr.gray, [x, y, blk_sz, blk_sz])

        width, height = self.screen.width, self.screen.height
        # draw border if view point reach the map border
        if viewX > self.width - self.screen.width_blocks:
            # right border
            pygame.draw.rect(surface, clr.black, (width - blk_sz, 0, blk_sz, height))
        elif viewX < 0:
            # left border
            pygame.draw.rect(surface, clr.black, (0, 0, blk_sz, height))

        if viewY > self.height - self.screen.height_blocks:
            # bottom border
            pygame.draw.rect(surface, clr.black, (0, height - blk_sz, width, blk_sz))
        elif viewY < 0:
            # top border
            pygame.draw.rect(surface, clr.black, (0, 0, width, blk_sz))

class EnviromentController:
    def __init__(self, screen_info):
        self.surface = None

        self.screen = screen_info

        self.ground = None

    def change_surface(self, surface):
        self.surface = surface
        self.change_screen_size()

    def change_screen_size(self):
        self.ground.change_screen_size()

    def load(self, filename):
        with open(filename) as file:
            read = file.read()
        info = read.split("\n")
        width, height = info[0].split("x")
        width, height = int(width), int(height)

        map_ = []
        draw_index = {}
        for i in range(1, len(info)):
            col = []
            for count, e in enumerate(info[i]):
                if e != GRASS:
                    if i - 1 not in draw_index:
                        draw_index[i - 1] = {}
                    draw_index[i - 1][count] = e
                col.append(e)
            map_.append(col)

        self.ground = Layer(GROUND, map_, width, height, draw_index, self.screen)

    def in_y_view(self, viewY):
        if viewY <= self.ground.width - self.screen.width_blocks:
            return True
        return False

    def in_x_view(self, viewX):
        if viewX <= self.ground.height - self.screen.height_blocks:
            return True
        return False

    def render(self, viewX, viewY):
        self.ground.render(self.surface, viewX, viewY)

    def stop(self):
        # delete all extend blackground
        path = os.getcwd() + "/texture/extend"
        for the_file in os.listdir(path):
            file_path = os.path.join(path, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except:
                pass

