import pygame
import os
import json
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

ANIMAL_ROLE_DISTANCE = 6

class AnimalInfo:
    def __init__(self):
        self.infos = {}
        self.drops = {}

    def load(self, file, images):
        path = os.getcwd()
        with open(os.path.join(path, file)) as file:
            read = file.read()
        info = json.loads(read)

        texture_dir = os.path.join("texture", "animal")

        for id_, animal in info.items():
            self.infos[id_] = {}
            self.infos[id_]["name"] = animal["name"]
            self.infos[id_]["step"] = animal["step"]
            self.infos[id_]["src"] = images[f"{texture_dir}/{animal['src']}"]

            self.drops[id_] = {}
            self.drops[id_]["wild"] = animal["wild"]
            self.drops[id_]["slaught"] = animal["slaught"]
            self.drops[id_]["farm"] = animal["farm"]

    def count_drops(self, animal_type, count):
        items = {}
        for drops in self.drops[animal_type]["farm"]:
            min_, max_ = drops["min"], drops["max"]
            items[drops["item"]] = sum([randint(min_, max_) for i in range(count)])
        return items

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

    def move(self, tick_interval):
        self.steps -= 1

        if self.direction == LEFT:
            self.x -= self.step * tick_interval
        elif self.direction == RIGHT:
            self.x += self.step * tick_interval
        elif self.direction == UP:
            self.y -= self.step * tick_interval
        elif self.direction == DOWN:
            self.y += self.step * tick_interval

        if self.steps == 0:
            self.rest(tick_interval)

    def rest(self, tick_interval):
        self.direction = None
        s =  int(0.5 / tick_interval)
        self.rest_time = randint(s, 3 / tick_interval)

    def decideDirection(self):
        self.direction = randint(1, 4)
        self.steps = randint(5, 10) * self.step

    def changeDriection(self):
        self.direction = randint(1, 4)

class Cow(AnimalBasic):
    def __init__(self, x, y, tamed):
        super().__init__(x, y, tamed, COW)
        self.step = 6

class Sheep(AnimalBasic):
    def __init__(self, x, y, tamed):
        super().__init__(x, y, tamed, SHEEP)
        self.step = 4

class Chicken(AnimalBasic):
    def __init__(self, x, y, tamed):
        super().__init__(x, y, tamed, CHICKEN)
        self.step = 2

class AnimalController:
    def __init__(self, screen_info, animal_info, images):
        self.screen = screen_info
        self.animal_info = animal_info
        self.surface = None
        self.envCtlr = None
        self.roleCtlr = None
        self.images = images

        self.animals = []
        self.textures = {}

        for animal_type in animal_info.infos.keys():
            self.textures[animal_type] = {}

    def setUpCtlr(self, envCtlr, roleCtlr):
        self.envCtlr = envCtlr
        self.roleCtlr = roleCtlr

    def change_surface(self, surface):
        self.surface = surface

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

    def tick_load(self, tick_interval):
        # tick_interval default is 0.1
        # move = 10 * tick_interval
        for animal in self.animals:
            if animal.tamed == True:
                continue

            if not animal.direction:
                if animal.rest_time > 0:
                    animal.rest_time -= 1
                else:
                    animal.decideDirection()

            else:
                tick_step = animal.step * tick_interval
                passed = True

                if animal.direction == LEFT:
                    if int(animal.x) == 0:
                        passed = False

                    else:
                        try:
                            if int(animal.x - tick_step) in self.envCtlr.ground.forbidden[int(animal.y)]:
                                passed = False
                        except:
                            pass

                    if passed:
                        for role in self.roleCtlr.roles.values():
                            now_distance = count_distance(animal.x, animal.y, role.x, role.y)

                            if now_distance < ANIMAL_ROLE_DISTANCE:
                                next_distance = count_distance(animal.x - tick_step, animal.y, role.x, role.y)
                                if now_distance > next_distance:
                                    passed = False
                                animal.steps += 1

                elif animal.direction == RIGHT:
                    if int(animal.x) == self.envCtlr.ground.max_x - 1:
                        passed = False

                    try:
                        if int(animal.x + 1 + tick_step) in self.envCtlr.ground.forbidden[int(animal.y)]:
                            passed = False
                    except:
                        pass

                    if passed:
                        for role in self.roleCtlr.roles.values():
                            now_distance = count_distance(animal.x, animal.y, role.x, role.y)

                            if now_distance < ANIMAL_ROLE_DISTANCE:
                                next_distance = count_distance(animal.x + tick_step, animal.y, role.x, role.y)
                                if now_distance > next_distance:
                                    passed = False
                                animal.steps += 1

                elif animal.direction == UP:
                    if int(animal.y) == 0:
                        passed = False

                    try:
                        if int(animal.x) in self.envCtlr.ground.forbidden[int(animal.y - tick_step)]:
                            passed = False
                    except:
                        pass

                    if passed:
                        for role in self.roleCtlr.roles.values():
                            now_distance = count_distance(animal.x, animal.y, role.x, role.y)

                            if now_distance < ANIMAL_ROLE_DISTANCE:
                                next_distance = count_distance(animal.x, animal.y - tick_step, role.x, role.y)
                                if now_distance > next_distance:
                                    passed = False
                                animal.steps += 1

                elif animal.direction == DOWN:
                    if int(animal.y) == self.envCtlr.ground.max_y - 1:
                        passed = False
                    try:
                        if int(animal.x) in self.envCtlr.ground.forbidden[int(animal.y + 1 + tick_step)]:
                            passed = False
                    except:
                        pass

                    if passed:
                        for role in self.roleCtlr.roles.values():
                            now_distance = count_distance(animal.x, animal.y, role.x, role.y)

                            if now_distance < ANIMAL_ROLE_DISTANCE:
                                next_distance = count_distance(animal.x, animal.y + tick_step, role.x, role.y)
                                if now_distance > next_distance:
                                    passed = False
                                animal.steps += 1

                if not passed:
                    animal.changeDriection()
                    continue

                animal.move(tick_interval)

    def render(self, viewX, viewY):
        if self.envCtlr.present_layer.type != 0:
            return

        blk_sz = self.screen.block_size

        for animal in self.animals:
            if animal.x >= viewX and animal.x - viewX < self.screen.width_blocks:
                if animal.y >= viewY and animal.y - viewY < self.screen.height_blocks:
                    x = (animal.x - viewX) * blk_sz
                    y = (animal.y - viewY) * blk_sz

                    if blk_sz not in self.textures[animal.type]:
                        self.textures[animal.type][blk_sz] = pygame.transform.scale(
                            self.animal_info.infos[animal.type]["src"],
                            (blk_sz, blk_sz),
                            )

                    self.surface.blit(self.textures[animal.type][blk_sz], (x, y))
