import pygame
import os
from color import clr

from pygame_extendtion import *

GRASS = "0"
ROCK = "1"
TREE = "2"

GROUND = 0
UNDERGROUND = 1

class Layer:
    def __init__(self, screen, type_=None, map_=None, width=None, height=None, draw_index=None):
        self.type = type_
        self.map = map_
        self.width = width
        self.height = height
        self.draw_index = draw_index
        self.forbidden = {}

        self.max_x = None
        self.max_y = None

        self.screen = screen

        # self.stone = pygame.image.load("texture/stone.png")
        if type_ == GROUND:
            self.image_source = pygame.image.load("texture/grass.png")
            self.texture = "grass"

    def load(self, layerfile):
        with open(layerfile) as file:
            read = file.read()
        info = read.split("\n")
        self.width, self.height = [int(i) for i in info[0].split("x")]
        self.type = int(info[1])

        self.map = []
        self.draw_index = {}
        for i in range(2, len(info)):
            col = []
            for count, e in enumerate(info[i]):
                if e != GRASS:
                    if i - 2 not in self.draw_index:
                        self.draw_index[i - 2] = {}
                    self.draw_index[i - 2][count] = e

                    if i - 2 not in self.forbidden:
                        self.forbidden[i - 2] = set()
                    self.forbidden[i - 2].add(count)
                col.append(e)
            self.map.append(col)

        self.max_x = len(self.map[0])
        self.max_y = len(self.map)

        if self.type == GROUND:
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
                            # surface.blit(self.stone, (x, y))
                            pygame.draw.rect(surface, clr.gray, [x, y, blk_sz, blk_sz])
                        elif cell == TREE:
                            pygame.draw.rect(surface, clr.brown, [x, y, blk_sz, blk_sz])

        width, height = self.screen.width, self.screen.height
        # draw border if view point reach the map border
        if viewX > self.width - self.screen.width_blocks:
            pygame.draw.rect(surface, clr.black, (width - blk_sz, 0, blk_sz, height))
        elif viewX < 0:
            pygame.draw.rect(surface, clr.black, (0, 0, blk_sz, height))

        if viewY > self.height - self.screen.height_blocks:
            pygame.draw.rect(surface, clr.black, (0, height - blk_sz, width, blk_sz))
        elif viewY < 0:
            pygame.draw.rect(surface, clr.black, (0, 0, width, blk_sz))

class EnviromentController:
    def __init__(self, screen_info):
        self.screen = screen_info
        self.surface = None

        self.ground = None
        self.present_layer = None

    def change_surface(self, surface):
        self.surface = surface
        self.change_screen_size()

    def change_screen_size(self):
        self.ground.change_screen_size()

    def change_map(self, pos, block_id, layer=None):
        if layer == None:
            layer = self.present_layer

        row, col = pos
        layer.map[col][row] = block_id

        layer.draw_index[col][row] = block_id

    def load(self, mappath):
        path = os.getcwd()
        path = os.path.join(path, mappath, "ground.txt")

        if not os.path.isfile(path):
            raise Exception(f"path {path} not exist")
        # load diffrent layer
        self.ground = Layer(self.screen)
        self.ground.load(path)

        self.present_layer = self.ground

    def in_y_view(self, viewY):
        if viewY <= self.ground.height - self.screen.height_blocks:
            return True
        return False

    def in_x_view(self, viewX):
        if viewX <= self.ground.width - self.screen.width_blocks:
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

