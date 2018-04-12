import pygame
import os
import json
from color import clr

from role import Inventory, InventoryItem
from animal import COW, SHEEP, CHICKEN
from pygame_extendtion import *

from random import randint

F_UP = 0
F_DOWN = 1
F_LEFT = 2
F_RIGHT = 3

class BuildingInfo:
    def __init__(self):
        self.buildings = {}

        # self.bd_box_src = None
        self.bd_boxes = {}

        # self.ovrlp_bd_box_src = None
        self.ovrlp_bd_boxes = {}

        self.resource_need = {}
        self.build_time = {}

    def load(self, file, images):
        path = os.getcwd()
        with open(os.path.join(path, file)) as file:
            read = file.read()
        self.buildings = json.loads(read)

        texture_dir = os.path.join("texture", "building")

        self.bd_box_src = images[texture_dir + "/bounding_box.png"]
        self.ovrlp_bd_box_src = images[texture_dir + "/overlap_bounding_box.png"]

        for i, building in self.buildings.items():
            if not isinstance(building, dict):
                continue

            self.buildings[i]["building_src"] = images[f"{texture_dir}/{building['building_src']}"]
            self.buildings[i]["icon_src"] = pygame.transform.scale(
                images[f"{texture_dir}/icon/{building['icon_src']}"],
                (30, 30))

            self.resource_need[i] = building["build_need"]
            self.build_time[i] = building["build_time"]

            self.__setattr__(building["name"].upper(), i)

class BluePrint:
    __type__ = "blueprint"

    def __init__(self, type_, pos, facing, build_info):
        build = build_info.buildings[type_]

        self.type = type_

        self.hitbox_lt = tuple(pos)
        self.width = build["width"]
        self.height = build["height"]

        self.facing = facing

        if self.facing == F_UP:
            self.width, self.height = self.height, self.width

            self.hitbox_lt = (pos[0], pos[1] - self.height + 1)

        elif self.facing == F_DOWN:
            self.width, self.height = self.height, self.width

            self.hitbox_lt = (pos[0] - self.width + 1, pos[1])

        elif self.facing == F_LEFT:
            self.hitbox_lt = (
                pos[0] - self.width + 1,
                pos[1] - self.height + 1)

        self.hitbox_rd = (
            self.hitbox_lt[0] + self.width,
            self.hitbox_lt[1] + self.height)

        self.resource = {}

    def __repr__(self):
        return f"{self.type} {self.hitbox_lt} {self.facing}"

    def click(self, pos, viewX, viewY, blk_sz):
        x, y = pos

        if x < (self.hitbox_lt[0] - viewX) * blk_sz:
            return False
        if x > (self.hitbox_rd[0] - viewX) * blk_sz:
            return False

        if y < (self.hitbox_lt[1] - viewY) * blk_sz:
            return False
        if y > (self.hitbox_rd[1] - viewY) * blk_sz:
            return False

        return True

    def render(self, surface, blk_sz, viewX, viewY):
        x = (self.hitbox_lt[0] - viewX) * blk_sz
        y = (self.hitbox_lt[1] - viewY) * blk_sz

        pygame.draw.rect(
            surface,
            clr.blue,
            (x, y, self.width * blk_sz, self.height * blk_sz, ),
            blk_sz // 10)

    def reach_resrc_need(self, resource_need):
        for r, c in resource_need.items():
            if r not in self.resource:
                self.resource[r] = 0
            if self.resource[r] != c:
                return False
        return True

    def put_resrc(self, inventory, resource_need):
        resrc_put = {}
        for r, c in resource_need.items():
            if r not in self.resource:
                self.resource[r] = 0
            if self.resource[r] != c:
                resource_add = c - self.resource[r]
                invtory_have = inventory.count_item(r)

                if invtory_have >= resource_add:
                    self.resource[r] = c
                    resrc_put[r] = resource_add
                else:
                    self.resource[r] += invtory_have
                    resrc_put[r] = invtory_have
        return resrc_put

    @staticmethod
    def parse(string, build_info):
        type_, pos, facing, resrouce, progress = string.split()

        pos = [int(i) for i in pos.split(",")]
        facing = int(facing)

        return BluePrint(type_, pos, facing, build_info)

class Building_Base:
    @classmethod
    def transfer(cls, building_value):
        datas = {}
        for data, type_ in cls.DATA_LIST.items():
            try:
                datas[data] = building_value[data]
            except:
                if type_ != None:
                    datas[data] = type_()
                else:
                    datas[data] = None
        return cls.DATA_LIST, datas

class Storage(Building_Base):
    DATA_LIST = {"inventory": Inventory}

class Farm(Building_Base):
    DATA_LIST = {
        "inventory": Inventory,
        "animals": dict,
        "tick": int,
        "random_tick": int,
        "animal_info": BuildingInfo
        }

    @staticmethod
    def animal_str_parse(string):
        l = string.split("|")

        aniamls = {}
        for i in l:
            if i == "N":
                continue

            t, c = i.split(",")
            aniamls[t] = int(c)

        return aniamls

class Mine(Building_Base):
    DATA_LIST = {
        "depth": int,
        "max_depth": int,
        "exit": bool,
        }

class Smelter(Building_Base):
    DATA_LIST = {
        "jobs": list,
        "doing": None,
        }

class Forge(Building_Base):
    DATA_LIST = {
        "jobs": list,
        "doing": None,
        }

class Building:
    __type__ = "building"

    def __init__(self, type_, pos, facing, build_info, building_value):
        build = build_info.buildings[type_]

        self.type = type_

        self.inherit_data_types = {}
        values = {}

        if type_ == build_info.STORAGE:
            self.inherit_data_types, values = Storage.transfer(building_value)

        elif type_ == build_info.FARM:
            self.inherit_data_types, values = Farm.transfer(building_value)

        elif type_ == build_info.MINE:
            building_value["max_depth"] = 10
            self.inherit_data_types, values = Mine.transfer(building_value)

        elif type_ == build_info.SMELTER:
            self.inherit_data_types, values = Smelter.transfer(building_value)

        elif type_ == build_info.FORGE:
            self.inherit_data_types, values = Forge.transfer(building_value)

        for name, value in values.items():
            self.__setattr__(name, value)

        src = build_info.buildings[type_]["building_src"]
        self.hitbox_lt = tuple(pos)
        self.width = build["width"]
        self.height = build["height"]

        self.facing = facing

        if self.facing == F_UP:
            self.width, self.height = self.height, self.width

            self.src = pygame.transform.rotate(src, 90)
            self.hitbox_lt = (pos[0], pos[1] - self.height + 1)

        elif self.facing == F_DOWN:
            self.width, self.height = self.height, self.width

            self.src = pygame.transform.rotate(src, -90)
            self.hitbox_lt = (pos[0] - self.width + 1, pos[1])

        elif self.facing == F_RIGHT:
            self.src = src

        if self.facing == F_LEFT:
            self.src = pygame.transform.rotate(src, 180)
            self.hitbox_lt = (
                pos[0] - self.width + 1,
                pos[1] - self.height + 1)

        self.hitbox_rd = (
            self.hitbox_lt[0] + self.width,
            self.hitbox_lt[1] + self.height)

        self.src_sized = {}

    def click(self, pos, viewX, viewY, blk_sz):
        x, y = pos

        if x < (self.hitbox_lt[0] - viewX) * blk_sz:
            return False
        if x > (self.hitbox_rd[0] - viewX) * blk_sz:
            return False

        if y < (self.hitbox_lt[1] - viewY) * blk_sz:
            return False
        if y > (self.hitbox_rd[1] - viewY) * blk_sz:
            return False

        return True

    def render(self, surface, images, blk_sz, viewX, viewY):
        x = (self.hitbox_lt[0] - viewX) * blk_sz
        y = (self.hitbox_lt[1] - viewY) * blk_sz

        if blk_sz not in self.src_sized:
            self.src_sized[blk_sz] = pygame.transform.scale(self.src,
                (self.width * blk_sz, self.height * blk_sz))

        surface.blit(self.src_sized[blk_sz], (x, y))

        if "animals" in self.inherit_data_types:
            for type_ in self.animals:
                y += blk_sz

                surface.blit(self.animal_info.infos[type_]["src"], (x + 10, y))

    @staticmethod
    def from_blueprint(blueprint, build_info, animal_info):
        building_value = {
            "inventory": Inventory.empty_infinite(),
            }
        if blueprint.type == build_info.FARM:
            building_value["animal_info"] = animal_info

        return Building(
            blueprint.type,
            blueprint.hitbox_lt,
            blueprint.facing,
            build_info,
            building_value
            )

    @staticmethod
    def parse(string, build_info, animal_info):
        type_, pos, facing, *building_value = string.split()

        pos = [int(i) for i in pos.split(",")]

        facing = int(facing)

        if type_ == build_info.STORAGE:
            building_value = dict(zip(
                ("inventory", ),
                building_value))
            building_value["inventory"] = Inventory.parse(building_value["inventory"], limit=-1)

        elif type_ == build_info.FARM:
            building_value = dict(zip(
                ("inventory", "animals", ),
                building_value))
            building_value["inventory"] = Inventory.parse(building_value["inventory"])
            building_value["animals"] = Farm.animal_str_parse(building_value["animals"])

            building_value["animal_info"] = animal_info
        elif type_ == build_info.MINE:
            building_value = dict()

        elif type_ == build_info.SMELTER:
            building_value = dict()

        return Building(type_,
            pos, 
            facing,
            build_info,
            building_value)

class BuildingController:
    def __init__(self, screen_info, images, build_info, items_info, animal_info):
        self.screen = screen_info
        self.images = images
        self.build_info = build_info
        self.items_info = items_info
        self.animal_info = animal_info
        self.surface = None

        self.buildings = {}
        self.blueprints = {}

        self.occupied = {}

    def __getitem__(self, key):
        return self.buildings[key]

    def setUpCtlr(self, envCtlr):
        self.envCtlr = envCtlr

    def change_surface(self, surface):
        self.surface = surface

    def check_overlap(self, blocks, pos):
        blk_sz = self.screen.block_size
        for block in blocks:
            x = block[0] + pos[0] // blk_sz
            y = block[1] + pos[1] // blk_sz

            try:
                if x in self.occupied[y]:
                    return True
            except:
                pass
        return False

    def load(self, mappath):
        path = os.getcwd()
        path = os.path.join(path, mappath, "building.txt")

        if not os.path.isfile(path):
            raise Exception(f"path {path} not exist")

        with open(path) as file:
            read = file.read()
        buildings = read.split("\n")

        for i in buildings:
            if i.find("bd-") >= 0:
                building = Building.parse(i[i.find("bd-") + 3:],
                    self.build_info,
                    self.animal_info)
                self.buildings[id(building)] = building

                hitbox_lt = building.hitbox_lt
                hitbox_rd = building.hitbox_rd

                for col in range(hitbox_lt[1], hitbox_rd[1]):
                    for row in range(hitbox_lt[0], hitbox_rd[0]):
                        if col not in self.occupied:
                            self.occupied[col] = set([])

                        self.occupied[col].add(row)
            elif i.find("bp-") >= 0:
                blueprint = BluePrint.parse(i[i.find("bp-") + 3:], self.build_info)
                self.blueprints[id(blueprint)] = blueprint

    def new_blueprint(self, blueprint):
        self.blueprints[id(blueprint)] = blueprint

    def finish_blueprint(self, blueprint_id):
        blueprint = self.blueprints[blueprint_id]

        building = Building.from_blueprint(blueprint,
            self.build_info,
            self.animal_info)
        self.buildings[id(building)] = building

        self.blueprints.pop(blueprint_id)

        hitbox_lt = building.hitbox_lt
        hitbox_rd = building.hitbox_rd

        for col in range(hitbox_lt[1], hitbox_rd[1]):
            for row in range(hitbox_lt[0], hitbox_rd[0]):
                if col not in self.occupied:
                    self.occupied[col] = set([])

                self.occupied[col].add(row)

    def tick_load(self, tick_interval):
        for building in self.buildings.values():
            if building.type == self.build_info.FARM:
                if building.random_tick == 0:
                    building.random_tick = randint(2, 3)
                else:
                    building.tick += 1
                    if building.tick * tick_interval == building.random_tick:
                        total_drops = {}
                        for type_, count in building.animals.items():
                            drops = self.animal_info.count_drops(type_, count)
                            for t, c in drops.items():
                                if t not in total_drops:
                                    total_drops[t] = 0
                                total_drops[t] += c
                        for t, c in total_drops.items():
                            t = self.items_info.__getattribute__(t.upper())
                            building.inventory.add(t, c)

                        building.tick = 0
                        building.random_tick = 0

    def click(self, x, y, viewX, viewY):
        if self.envCtlr.present_layer.type == 0:
            for blueprint in self.blueprints.values():
                if blueprint.click((x, y), viewX, viewY, self.screen.block_size):
                    return blueprint

            for building in self.buildings.values():
                if building.click((x, y), viewX, viewY, self.screen.block_size):
                    return building

    def render(self, viewX, viewY):
        if self.envCtlr.present_layer.type != 0:
            return

        blk_sz = self.screen.block_size
        for blueprint in self.blueprints.values():
            blueprint.render(self.surface, blk_sz, viewX, viewY)

        for building in self.buildings.values():
            building.render(self.surface, self.images, blk_sz, viewX, viewY)
