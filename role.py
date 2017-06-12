import pygame
import os
from color import clr
import math

from random import randint
from pygame_extendtion import *


class WORK:
    BUILD = "working_build"
    CHOP = "working_chop_tree"
    MOVEITEM = "working_move_item"
    MOVE = "working_move"
    PRODUCE = "working_produce"

class InventoryItem:
    def __init__(self, type_, count, forced):
        self.type = type_
        self.count = count
        self.forced = forced

    def __repr__(self):
        return f"{self.type} {self.count} {self.forced}"

class Inventory:
    def __init__(self):
        self.slots = []

    def parse(self, string):
        items = string.split("|")
        self.slots = []

        for item in items:
            if item == "N":
                self.slots.append(None)
            else:
                type_, count, forced = item.split(",")
                count = int(count)

                if forced == "t":
                    forced = True
                else:
                    forced = False
                self.slots.append(InventoryItem(type_, count, forced))

    def __len__(self):
        return 10 - self.slots.count(None)

    def __getitem__(self, key):
        return self.slots[key]

    def add(self, type_, count):
        type_slot = []
        empty_slots = []
        for i, slot in enumerate(self.slots):
            if slot == None:
                empty_slots.append(i)
            elif slot.type == type_:
                type_slot.append(i)

        if len(empty_slots) == len(self.slots):
            time = math.ceil(count / 50)

            if time > len(empty_slots):
                for i in empty_slots:
                    self.slots[i] = InventoryItem(type_, 50, False)
                return count - (50 * len(empty_slots))
            else:
                i = -1
                for i in range(time - 1):
                    self.slots[empty_slots[i]] = InventoryItem(type_, 50, False)

                self.slots[empty_slots[i + 1]] = InventoryItem(type_, count - (50 * (time - 1)), False)
                return 0
        elif len(type_slot) != 0:
            for i in type_slot:
                if count + self.slots[i].count <= 50:
                    self.slots[i].count += count
                    count = 0
                    break
                elif self.slots[i].count < 50:
                    count -= (50 - self.slots[i].count)
                    self.slots[i].count = 50

        if count > 0:
            time = math.ceil(count / 50)

            if time > len(empty_slots):
                for i in empty_slots:
                    self.slots[i] = InventoryItem(type_, 50, False)
                return count - (50 * len(empty_slots))
            else:
                i = -1
                for i in range(time - 1):
                    self.slots[empty_slots[i]] = InventoryItem(type_, 50, False)

                self.slots[empty_slots[i + 1]] = InventoryItem(type_, count - (50 * (time - 1)), False)
                return 0
        else:
            return 0

class Working:
    def __init__(self, type_, work_with_id):
        self.type = type_
        self.work_with_id = work_with_id

        self.progress = 0

        if type_ == WORK.CHOP:
            self.progress_need = 1

    def __repr__(self):
        return f"{self.type} {self.work_with_id}"

    def parse(self):
        pass

class Role:
    def __init__(self, id_, x, y, working, inventory):
        self.id = id_
        self.x = x
        self.y = y
        self.working = working
        self.inventory = inventory

        self.step = 6

    def __repr__(self):
        return f"{self.id}"

    def move(self, pos, tick_interval):
        x, y = pos
        step = self.step * tick_interval
        if self.x != x:
            if math.fabs(x - self.x) < step:
                self.x = x
            else:
                self.x += Role.direction(x, self.x) * step
        elif self.y != y:
            if math.fabs(y - self.y) < step:
                self.y = y
            else:
                self.y += Role.direction(y, self.y) * step
        else:
            return True
        return False

    @staticmethod
    def direction(point1, point2):
        if point1 > point2:
            return 1
        return -1


class RoleController:
    def __init__(self, screen_info):
        self.screen = screen_info
        self.evnCtlr = None
        self.BuildingCtrl = None
        self.surface = None

        self.roles = {}
        self.role_img_src = None
        self.role_textures = {}

    def setUpCtrl(self, evnCtlr):
        self.evnCtlr = evnCtlr

    def change_surface(self, surface):
        self.surface = surface

    def new_work(self, role_id, type_, work_with_id):
        self.roles[role_id].working = Working(type_, work_with_id)

    def load(self, mappath):
        path = os.getcwd()
        path = os.path.join(path, mappath, "role.txt")

        if not os.path.isfile(path):
            raise Exception(f"path {path} not exist")

        with open(path) as file:
            read = file.read()
        roles_list = read.split("\n")

        for role_info in roles_list:
            role_info = role_info.split()
            inventory_info = role_info[-1]
            working_info = role_info[-2]
            id_, x, y = [int(i) for i in role_info[:-2]]

            inventory = Inventory()
            inventory.parse(inventory_info)

            # working = Working()
            # working.parse(working_info)

            self.roles[id_] = Role(id_, x, y, None, inventory)

        self.role_img_src = pygame.image.load("texture/role.png")

    def tick_load(self, tick_interval):
        for role in self.roles.values():
            if role.working != None:
                if role.working.type == WORK.CHOP:
                    right_posistion = role.move(role.working.work_with_id, tick_interval)
                    if right_posistion:
                        if int(role.working.progress) == role.working.progress_need:
                            self.evnCtlr.change_map(role.working.work_with_id, "0")

                            role.inventory.add("7", randint(10, 30))
                            role.working = None
                        else:
                            role.working.progress += tick_interval

    def render(self, viewX, viewY):
        blk_sz = self.screen.block_size

        for role in self.roles.values():
            if role.x >= viewX and role.x - viewX < self.screen.width_blocks:
                if role.y >= viewY and role.y - viewY < self.screen.height_blocks:
                    x = (role.x - viewX) * blk_sz
                    y = (role.y - viewY) * blk_sz

                    if blk_sz not in self.role_textures:
                        self.role_textures[blk_sz] = pygame.transform.scale(
                            self.role_img_src,
                            (blk_sz, blk_sz),
                            )
                    self.surface.blit(self.role_textures[blk_sz], (x, y))
