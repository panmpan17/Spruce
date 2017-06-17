import pygame
import os
import json
from color import clr

from role import Inventory, InventoryItem
from pygame_extendtion import *

F_UP = 0
F_DOWN = 1
F_LEFT = 2
F_RIGHT = 3

class BuildingInfo:
    def __init__(self):
        self.buildings = {}

        self.bd_box_src = None
        self.bd_boxes = {}

        self.ovrlp_bd_box_src = None
        self.ovrlp_bd_boxes = {}

        self.resource_need = {}
        self.build_time = {}

    def load(self, file):
        path = os.getcwd()
        with open(os.path.join(path, file)) as file:
            read = file.read()
        self.buildings = json.loads(read)


        ITEM_TEXTURE_DIR = os.path.join(path, "texture", "building")

        self.bd_box_src = pygame.image.load(os.path.join(ITEM_TEXTURE_DIR, self.buildings["bd_box"]))
        self.buildings.pop("bd_box")

        self.ovrlp_bd_box_src = pygame.image.load(os.path.join(ITEM_TEXTURE_DIR, self.buildings["ovrlp_bd_box"]))
        self.buildings.pop("ovrlp_bd_box")

        for i, building in self.buildings.items():
            if not isinstance(building, dict):
                continue

            building_src = os.path.join(ITEM_TEXTURE_DIR, building["building_src"])
            icon_src = os.path.join(ITEM_TEXTURE_DIR, "icon", building["icon_src"])

            if os.path.isfile(building_src):
                self.buildings[i]["building_src"] = pygame.image.load(building_src)
            if os.path.isfile(icon_src):
                self.buildings[i]["icon_src"] = pygame.transform.scale(
                    pygame.image.load(icon_src),
                    (30, 30))

            self.resource_need[i] = building["build_need"]
            self.build_time[i] = building["build_time"]

            self.__setattr__(building["name"].upper(), i)

class BluePrint:
    def __init__(self, type_, pos, facing, build_info):
        self.type = type_
        self.pos = pos
        self.facing = facing

        build = build_info.buildings[type_]
        self.width = build["width"]
        self.height = build["height"]

        self.resource = {}

    def __repr__(self):
        return f"{self.type} {self.pos} {self.facing}"

    def render(self, surface, blk_sz, viewX, viewY):
        x, y = self.pos
        x = (x - viewX) * blk_sz
        y = (y - viewY) * blk_sz

        w = 0
        h = 0
        if self.facing == F_RIGHT:
            w = self.width * blk_sz
            h = self.height * blk_sz
        elif self.facing == F_DOWN:
            w = self.height * blk_sz
            h = self.width * blk_sz
            x = x - w + blk_sz
        elif self.facing == F_LEFT:
            w = self.width * blk_sz
            h = self.height * blk_sz
            x = x - w + blk_sz
            y = y - h + blk_sz
        elif self.facing == F_UP:
            w = self.height * blk_sz
            h = self.width * blk_sz
            y = y - h + blk_sz

        pygame.draw.rect(
            surface,
            clr.blue,
            (x, y, w, h, ),
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

class Building:
    def __init__(self, type_, pos, facing, build_info):
        self.type = type_
        self.facing = facing

        build = build_info.buildings[type_]

        src = build_info.buildings[type_]["building_src"]
        self.hitbox_lt = pos
        self.width = build["width"]
        self.height = build["height"]

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

    def render(self, surface, blk_sz, viewX, viewY):
        x = (self.hitbox_lt[0] - viewX) * blk_sz
        y = (self.hitbox_lt[1] - viewY) * blk_sz

        if blk_sz not in self.src_sized:
            self.src_sized[blk_sz] = pygame.transform.scale(self.src,
                (self.width * blk_sz, self.height * blk_sz))

        surface.blit(self.src_sized[blk_sz], (x, y))

    @staticmethod
    def from_blueprint(blueprint, build_info):
        return Building(
            blueprint.type,
            blueprint.pos,
            blueprint.facing,
            build_info
            )

    @staticmethod
    def parse(string, build_info):
        type_, pos, facing, invertory = string.split()

        pos = [int(i) for i in pos.split(",")]

        facing = int(facing)

        # inventory = Inventory.parse(invertory, limit=1)

        return Building(type_, pos, facing, build_info)

class BuildingController:
    def __init__(self, screen_info, build_info):
        self.screen = screen_info
        self.build_info = build_info
        self.surface = None

        self.buildings = {}
        self.blueprints = {}

        self.occupied = {}

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
                building = Building.parse(i[i.find("bd-") + 3:], self.build_info)
                self.buildings[id(building)] = building
            elif i.find("bp-") >= 0:
                blueprint = BluePrint.parse(i[i.find("bp-") + 3:], self.build_info)
                self.blueprints[id(blueprint)] = blueprint

    def new_blueprint(self, blueprint):
        self.blueprints[id(blueprint)] = blueprint

    def finish_blueprint(self, blueprint_id):
        blueprint = self.blueprints[blueprint_id]

        building = Building.from_blueprint(blueprint, self.build_info)
        self.buildings[id(building)] = building

        self.blueprints.pop(blueprint_id)

        hitbox_lt = building.hitbox_lt
        hitbox_rd = building.hitbox_rd

        for col in range(hitbox_lt[1], hitbox_rd[1]):
            for row in range(hitbox_lt[0], hitbox_rd[0]):
                if col not in self.occupied:
                    self.occupied[col] = set([])

                self.occupied[col].add(row)

    def render(self, viewX, viewY):
        blk_sz = self.screen.block_size
        for blueprint in self.blueprints.values():
            blueprint.render(self.surface, blk_sz, viewX, viewY)

        for building in self.buildings.values():
            building.render(self.surface, blk_sz, viewX, viewY)








