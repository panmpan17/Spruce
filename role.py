import pygame
import os
from color import clr

from random import randint
from pygame_extendtion import *

class InventoryItem:
    def __init__(self, type_, count, forced):
        self.type = type_
        self.count = count
        self.forced = forced

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
                type_, count = int(type_)
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


class Role:
    def __init__(self, id_, x, y, working_on, inventory):
        self.id = id_
        self.x = x
        self.y = y
        self.working_on = working_on
        self.inventory = inventory

    def __repr__(self):
        return f"{self.id}"

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
            id_, x, y, working_on = [int(i) for i in role_info[:-1]]

            inventory = Inventory()
            inventory.parse(inventory_info)

            self.roles[id_] = Role(id_, x, y, working_on, inventory)

        self.role_img_src = pygame.image.load("texture/role.png")

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

