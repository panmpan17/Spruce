import pygame
import os
from color import clr

from random import randint
from pygame_extendtion import *

COW = "1"
SHEEP = "2"
CHICKEN = "3"

RIGHT = 1
LEFT = 2
UP = 3
DOWN = 4

class AnimalBasic:
    def __init__(self, x, y, tamed, type_=None):
        self.x = x
        self.y = y
        self.tamed = tamed
        self.type = type_
        self.direction = None
        self.steps = 0
        self.rest_time = 0

    def __repr__(self):
        return f"{self.type} {self.tamed}"

    def move(self, tickInterval):
        self.steps -= 1

        if self.direction == LEFT:
            self.x -= self.step * tickInterval
        elif self.direction == RIGHT:
            self.x += self.step * tickInterval
        elif self.direction == UP:
            self.y -= self.step * tickInterval
        elif self.direction == DOWN:
            self.y += self.step * tickInterval

        if self.steps == 0:
            self.rest(tickInterval)

    def rest(self, tickInterval):
        self.direction = None
        self.rest_time = randint(1 / tickInterval, 1.5 / tickInterval)

    def decideDirection(self):
        self.direction = LEFT
        self.steps = randint(5, 15)

class Cow(AnimalBasic):
    def __init__(self, x, y, tamed):
        super().__init__(x, y, tamed, COW)
        self.step = 8

class Sheep(AnimalBasic):
    def __init__(self, x, y, tamed):
        super().__init__(x, y, tamed, SHEEP)
        self.step = 6

class Chicken(AnimalBasic):
    def __init__(self, x, y, tamed):
        super().__init__(x, y, tamed, CHICKEN)
        self.step = 4

class AnimalController:
    def __init__(self, screen_info):
        self.screen = screen_info
        self.surface = None
        self.envCtlr = None

        self.animals = []

    def setUpCtlr(self, envCtlr):
        self.envCtlr = envCtlr

    def change_surface(self, surface):
        self.surface = randint(1,4)
        self.change_screen_size()

    def change_screen_size(self):
        pass

    def load(self, mappath):
        path = os.getcwd()
        path = os.path.join(path, mappath, "animal.txt")

        if not os.path.isfile(path):
            raise Exception(f"path {path} not exist")

        with open(path) as file:
            read = file.read()
        animals_list = read.split("\n")

        for animal_info in animals_list:
            type_, x, y, tamed = animal_info.split()
            x, y = int(x), int(y)

            if tamed == "t":
                tamed = True
            else:
                tamed = False

            if type_ == COW:
                type_ = Cow
            elif type_ == SHEEP:
                type_ = Sheep
            elif type_ == CHICKEN:
                type_ = Chicken
            self.animals.append(type_(x, y, tamed))

        self.cow_img_src = pygame.image.load("texture/cow.png")
        self.cow_textures = {}

        self.sheep_img_src = pygame.image.load("texture/sheep.png")
        self.sheep_textures = {}

        self.chicken_img_src = pygame.image.load("texture/chicken.png")
        self.chicken_textures = {}

    def tick_load(self, tickInterval):
        # tickInterval default is 0.1
        # move = 10 * tickInterval
        for animal in self.animals:
            if not animal.direction:
                if animal.rest_time > 0:
                    animal.rest_time -= 1
                else:
                    animal.decideDirection()

            else:
                tick_step = animal.step * tickInterval
                if animal.direction == LEFT:
                    passed = True

                    if int(animal.x) == 0:
                        passed = False
                    try:
                        if int(animal.x - tick_step) in self.envCtlr.ground.forbidden[int(animal.y)]:
                            passed = False
                    except:
                        pass

                    if not passed:
                        animal.decideDirection()
                        continue
                elif animal.direction == RIGHT:
                    passed = True

                    if int(animal.x) == self.envCtlr.ground.max_x - 1:
                        passed = False
                    try:
                        if int(animal.x + 1 + tickInterval) in self.envCtlr.ground.forbidden[int(animal.y)]:
                            passed = False
                    except:
                        pass

                    if not passed:
                        animal.decideDirection()
                        continue
                elif animal.direction == UP:
                    passed = True

                    if int(animal.y) == 0:
                        passed = False
                    try:
                        if int(animal.x) in self.envCtlr.ground.forbidden[int(animal.y - tick_step)]:
                            passed = False
                    except:
                        pass

                    if not passed:
                        animal.decideDirection()
                        continue
                elif animal.direction == DOWN:
                    passed = True

                    if int(animal.y) == self.envCtlr.ground.max_y - 1:
                        passed = False
                    try:
                        if int(animal.x) in self.envCtlr.ground.forbidden[int(animal.y + 1 + tick_step)]:
                            passed = False
                    except:
                        pass

                    if not passed:
                        animal.decideDirection()
                        continue

                animal.move(tickInterval)
        pygame.event.post(MyPygameEvent.VBUPDATE)

    def render(self, viewX, viewY):
        blk_sz = self.screen.block_size

        for animal in self.animals:
            if animal.x >= viewX and animal.x - viewX < self.screen.width_blocks:
                if animal.y >= viewY and animal.y - viewY < self.screen.height_blocks:
                    x = (animal.x - viewX) * blk_sz
                    y = (animal.y - viewY) * blk_sz

                    blk_sz = self.screen.block_size
                    if animal.type == COW:
                        if blk_sz not in self.cow_textures:
                            self.cow_textures[blk_sz] = pygame.transform.scale(
                                self.cow_img_src,
                                (blk_sz, blk_sz),
                                )
                        self.surface.blit(self.cow_textures[blk_sz], (x, y))
                    elif animal.type == SHEEP:
                        if blk_sz not in self.sheep_textures:
                            self.sheep_textures[blk_sz] = pygame.transform.scale(
                                self.sheep_img_src,
                                (blk_sz, blk_sz),
                                )
                        self.surface.blit(self.sheep_textures[blk_sz], (x, y))
                    elif animal.type == CHICKEN:
                        if blk_sz not in self.chicken_textures:
                            self.chicken_textures[blk_sz] = pygame.transform.scale(
                                self.chicken_img_src,
                                (blk_sz, blk_sz),
                                )
                        self.surface.blit(self.chicken_textures[blk_sz], (x, y))
