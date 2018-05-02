import pygame
import os
from color import clr

from pygame_extendtion import *

AIR = "0"
ROCK = "1"
TREE = "2"
COAL = "3"
COPPER = "4"
IRON = "5"
GOLD = "6"

GROUND = 0
UNDERGROUND = -1
EXIT = "exit"

RIGHT = (1, 0)
LEFT = (-1, 0)
UP = (0, 1)
DOWN = (0, -1)
ALL_DIRECTION = (RIGHT, LEFT, UP, DOWN)

class Layer:
    def __init__(self, screen, type_=None, map_=None, width=None, height=None, draw_index=None):
        self.type = type_
        self.map = map_
        self.width = width
        self.height = height
        self.draw_index = draw_index
        self.forbidden = {}

        self.bg = None

        self.max_x = None
        self.max_y = None

        self.screen = screen

    def change_block(self, pos, block):
        x, y = pos
        block_type = self.map[y][x]
        self.map[y][x] = block

        if block == AIR:
            if y in self.forbidden:
                self.forbidden[y].discard(x)
            if y in self.draw_index:
                if x in self.draw_index[y]:
                    print(type(self.draw_index))
                    self.draw_index[y].discard(x)
        else:
            if y not in self.forbidden:
                self.forbidden[y] = set()
            self.forbidden[y].add(x)
            self.draw_index[y][x] = block

        return block_type


    def check_overlap(self, blocks, pos):
        blk_sz = self.screen.block_size
        for block in blocks:
            x = block[0] + pos[0] // blk_sz
            y = block[1] + pos[1] // blk_sz

            if self.map[y][x] != AIR:
                return True
        return False

    def load(self, layerfile, images):
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
                if e != AIR:
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

        self.image_source = images["texture/grass.png"]
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

class UGLayer(Layer):
    def __init__(self, screen, type_=None, map_=None, width=None, height=None, draw_index=None):
        super().__init__(screen,
            type_=type_, map_=map_,
            width=width, height=height, draw_index=draw_index)

        self.edge = {}
        self.resized_img = {}
        self.exits = []

    def change_screen_size(self):
        pass

    def load(self, layerfile, images):
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
                if e == AIR:
                    if i - 2 not in self.draw_index:
                        self.draw_index[i - 2] = {}
                    self.draw_index[i - 2][count] = e

                col.append(e)
            self.map.append(col)

        self.max_x = len(self.map[0])
        self.max_y = len(self.map)

        self.image_source = images["texture/stone.png"]

    def render(self, surface, viewX, viewY):
        pygame.draw.rect(surface, clr.gray, [0, 0, self.screen.width, self.screen.height])

        blk_sz = self.screen.block_size
        for col in self.draw_index:
            # check col is in the range need to display
            if col >= viewY and col - viewY < self.screen.height_blocks:
                for row in self.draw_index[col]:
                    # check row is in the range need to display
                    if row >= viewX and row - viewX < self.screen.width_blocks:
                        y = (col - viewY) * blk_sz
                        x = (row - viewX) * blk_sz
                        # draw block texture

                        if blk_sz not in self.resized_img:
                            self.resized_img[blk_sz] = pygame.transform.scale(self.image_source,
                                (blk_sz, blk_sz))
                        surface.blit(self.resized_img[blk_sz], (x, y))

        for col in self.edge:
            # check col is in the range need to display
            if col >= viewY and col - viewY < self.screen.height_blocks:
                for row in self.edge[col]:
                    # check row is in the range need to display
                    if row >= viewX and row - viewX < self.screen.width_blocks:
                        y = (col - viewY) * blk_sz
                        x = (row - viewX) * blk_sz

                        cell = self.map[col][row]
                        # draw block texture
                        if cell == COAL:
                            pygame.draw.rect(surface, clr.black, [x, y, blk_sz, blk_sz])
                        elif cell == COPPER:
                            pygame.draw.rect(surface, clr.copper, [x, y, blk_sz, blk_sz])
                        elif cell == IRON:
                            pygame.draw.rect(surface, clr.white, [x, y, blk_sz, blk_sz])
                        elif cell == GOLD:
                            pygame.draw.rect(surface, clr.yellow, [x, y, blk_sz, blk_sz])
                        # surface.blit(self.image_source, (x, y))

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

    def change_block(self, pos, block_id):
        block_type = super().change_block(pos, block_id)

        if block_id == AIR:
            x, y = pos
            if y not in self.draw_index:
                self.draw_index[y] = set()
            self.draw_index[y].add(x)

            if y in self.edge:
                self.edge[y].discard(x)
            for xvec, yvec in ALL_DIRECTION:
                if not (0 <= (x + xvec) < self.width):
                    continue
                if not (0 <= (y + yvec) < self.height):
                    continue
                if y + yvec not in self.edge:
                    self.edge[y + yvec] = set()
                self.edge[y + yvec].add(x + xvec)

        return block_type

    def add_exit(self, pos1, pos2):
        self.exits.append((pos1, pos2))

class EnviromentController:
    def __init__(self, screen_info, images):
        self.screen = screen_info
        self.images = images
        self.surface = None

        self.ground = None
        self.underground = None
        self.layers = {}
        self.present_layer = None
        self.depth = 0

    def change_surface(self, surface):
        self.surface = surface
        self.change_screen_size()

    def change_screen_size(self):
        self.present_layer.change_screen_size()

    def change_map(self, location, pos, block_id):
        return self.layers[location].change_block(pos, block_id)

    def load(self, mappath):
        path = os.getcwd()
        path = os.path.join(path, mappath, "ground.txt")

        if not os.path.isfile(path):
            raise Exception(f"path {path} not exist")
        # load diffrent layer
        self.ground = Layer(self.screen)
        self.ground.load(path, self.images)

        path = os.getcwd()
        path = os.path.join(path, mappath, "underground.txt")

        if not os.path.isfile(path):
            raise Exception(f"path {path} not exist")
        # load diffrent layer
        self.underground = UGLayer(self.screen)
        self.underground.load(path, self.images)

        self.present_layer = self.ground
        self.layers[self.ground.type] = self.ground
        self.layers[self.underground.type] = self.underground

    def in_x_view(self, viewX):
        if viewX <= self.present_layer.width - self.screen.width_blocks:
            return True
        return False

    def in_y_view(self, viewY):
        if viewY <= self.present_layer.height - self.screen.height_blocks:
            return True
        return False

    def click(self, x, y, viewX, viewY):
        blk_sz = self.screen.block_size
        row = (x // blk_sz) + viewX
        col = (y // blk_sz) + viewY

        if self.present_layer.type == GROUND:
            if col in self.present_layer.draw_index:
                if row in self.present_layer.draw_index[col]:
                    block = self.present_layer.map[col][row]
                    return block, row, col
        else:
            for exit in self.present_layer.exits:
                pos1, pos2 = exit
                if pos1[0] <= row < pos2[0]:
                    if pos1[1] <= col < pos2[1]:
                        return EXIT, row, col

            if col in self.present_layer.edge:
                if row in self.present_layer.edge[col]:
                    block = self.present_layer.map[col][row]
                    return block, row, col
        return False

    def change_depth(self, depth, viewX, viewY):
        if depth == 1:
            if self.depth != 0:
                self.depth += 1
                self.present_layer = self.ground
            else:
                return viewX, viewY
        else:
            if self.depth != -1:
                self.depth -= 1
                self.present_layer = self.underground
            else:
                return viewX, viewY

        self.present_layer.change_screen_size()
        if not self.in_x_view(viewX):
            viewX = self.present_layer.width - self.screen.width_blocks
        if not self.in_y_view(viewY):
            viewY = self.present_layer.height - self.screen.height_blocks
        return viewX, viewY

    def dig_down(self, mine):
        if mine.exit:
            return self.underground.type
        x_range = range(mine.hitbox_lt[0], mine.hitbox_rd[0])
        y_range = range(mine.hitbox_lt[1], mine.hitbox_rd[1])
        self.underground.add_exit(mine.hitbox_lt, mine.hitbox_rd)

        for y in y_range:
            for x in x_range:
                self.underground.change_block((x, y), AIR)

        mine.exit = True
        return self.underground.type

    def render(self, viewX, viewY):
        self.present_layer.render(self.surface, viewX, viewY)

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

