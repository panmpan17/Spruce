import pygame
import os
import json
from color import clr

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

class BluePrint:
	def __init__(self, type_, pos, facing, build_info):
		self.type = type_
		self.pos = pos
		self.facing = facing

		build = build_info.buildings[type_]
		self.width = build["width"]
		self.height = build["height"]

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

class BuildingController:
	def __init__(self, screen_info, build_info):
		self.screen = screen_info
		self.build_info = build_info
		self.surface = None

		self.buildings = {}
		self.blueprints = []

	def change_surface(self, surface):
		self.surface = surface

	def load(self, mappath):
		path = os.getcwd()
		path = os.path.join(path, mappath, "building.txt")

		if not os.path.isfile(path):
			raise Exception(f"path {path} not exist")

	def new_blueprint(self, blueprint):
		self.blueprints.append(blueprint)

	def render(self, viewX, viewY):
		blk_sz = self.screen.block_size
		for blueprint in self.blueprints:
			blueprint.render(self.surface, blk_sz, viewX, viewY)







