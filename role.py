import pygame
import os
import math
from color import clr

from random import randint
from pygame_extendtion import *
from enviroment import AIR, ROCK, TREE, COAL, COPPER, IRON, GOLD
from work import WORK, Working

class InventoryItem:
    def __init__(self, type_, count, forced):
        self.type = type_
        self.count = count
        self.forced = forced

    def __repr__(self):
        return f"{self.type} {self.count} {self.forced}"

    @staticmethod
    def parse(self, string):
        info = string.split(",")

        type_ = info[0]
        count = info[1]

        forced = False
        if len(info) >= 3:
            forced = info[3]
            if forced == "t":
                forced = True
            else:
                forced = False

        return InventoryItem(type_, count, forced)

class Inventory:
    def __init__(self, slots=None, limit=10):
        self.slots = []

        if slots == None:
            for i in range(limit):
                self.slots.append(None)
        else:
            self.slots = slots
        self.limit = limit

    def __len__(self):
        return len(self.slots)

    def __getitem__(self, key):
        return self.slots[key]

    def __repr__(self):
        return str(self.slots)

    def add(self, type_, count):
        type_slot = []
        empty_slots = []
        extend_slots = []
        for i, slot in enumerate(self.slots):
            if slot == None:
                empty_slots.append(i)
            elif slot.type == type_:
                type_slot.append(i)

        if len(empty_slots) == len(self.slots):
            count = self.item_empty_slot(type_, count, empty_slots)
        elif len(type_slot) != 0:
            for i in type_slot:
                if count + self.slots[i].count <= 50:
                    self.slots[i].count += count
                    count = 0
                    break
                elif self.slots[i].count < 50:
                    count -= (50 - self.slots[i].count)
                    self.slots[i].count = 50

        if count > 0 and len(empty_slots) > 0:
            count = self.item_empty_slot(type_, count, empty_slots)

        # if inventory have no limit, add more slots
        if count > 0 and self.limit == -1:
            empty_slots = []
            start_index = len(self.slots)
            for i in range(math.ceil(count / 50)):
                self.slots.append(None)
                empty_slots.append(start_index + i)

            count = self.item_empty_slot(type_, count, empty_slots)
            return count
        else:
            return count

    def take(self, type_, count):
        slot_empty = []
        for i, slot in enumerate(self.slots):
            if slot == None:
                continue
            if slot.type == type_:
                if slot.forced:
                    if slot.count - 1 < count:
                        count -= slot.count - 1
                        slot.count = 1
                    else:
                        slot.count -= count
                        count = 0
                        break
                else:
                    if slot.count <= count:
                        slot_empty.append(i)
                        count -= slot.count
                    else:
                        slot.count -= count
                        count = 0
                        break

        if len(slot_empty) > 0:
            for i in slot_empty:
                self.slots[i] = None
        return count

    def count_item(self, type_):
        c = 0
        for slot in self.slots:
            if slot == None:
                continue
            if slot.type == type_:
                c += slot.count
        return c

    def item_empty_slot(self, type_, count, empty_slots):
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

    def check_empty_slot(self):
        return self.slots.count(None)

    def set_item_forced(self, item_index, forced):
        if self.slots[item_index] == None:
            return
        self.slots[item_index].forced = forced

    def check_item_forced(self, item_index):
        if self.slots[item_index] == None:
            return None
        return self.slots[item_index].forced

    def clear_item_index(self, item_index):
        if self.slots[item_index] == None:
            return None
        type_ = self.slots[item_index].type
        count = self.slots[item_index].count
        self.slots[item_index] = None
        return type_, count

    def clear_all_item(self, forced):
        count = {}
        slot_not_empty = []
        for i, slot in enumerate(self.slots):
            if slot == None:
                continue
            if (not forced) and slot.forced == True:
                continue

            if slot.type not in count:
                count[slot.type] = 0
            count[slot.type] += slot.count
            slot_not_empty.append(i)

        for slot in slot_not_empty:
            self.slots[slot] = None
        return count

    def transfer(self, inventory, forced=False):
        empty_slots = []
        for i, slot in enumerate(self.slots):
            if slot == None:
                continue
            if forced and slot.forced:
                continue
            count = inventory.add(slot.type, slot.count)
            if count > 0:
                slot.count = count
            else:
                empty_slots.append(i)
            self.slots[i] = None

    @staticmethod
    def parse(string, limit=None):
        items = string.split("|")
        slots = []

        for item in items:
            if item == "N":
                slots.append(None)
            else:
                type_, count, forced = item.split(",")
                count = int(count)

                if forced == "t":
                    forced = True
                else:
                    forced = False
                slots.append(InventoryItem(type_, count, forced))

        if limit == None:
            return Inventory(slots=slots, limit=len(slots))
        else:
            return Inventory(slots=slots, limit=limit)

    @staticmethod
    def empty_infinite():
        return Inventory(slots=[], limit=-1)

class Role:
    def __init__(self, id_, x, y, location, working, inventory):
        self.id = id_
        self.x = x
        self.y = y
        self.location = location
        self.working = working
        self.inventory = inventory

        self.step = 6

    def __repr__(self):
        return f"{self.id}"

    def move(self, pos, tick_interval):
        x, y = pos
        step = self.step * tick_interval
        if self.x != x:
            if math.fabs(x - self.x) <= step:
                self.x = x
                step -= math.fabs(x - self.x)
            else:
                self.x += Role.direction(x, self.x) * step
                step = 0
        if step > 0 and self.y != y:
            if math.fabs(y - self.y) < step:
                self.y = y
            else:
                self.y += Role.direction(y, self.y) * step
        if self.x == x and self.y == y:
            return True
        return False

    @staticmethod
    def direction(point1, point2):
        if point1 > point2:
            return 1
        return -1

class RoleController:
    def __init__(self, screen_info, images, build_info):
        self.screen = screen_info
        self.images = images
        self.build_info = build_info
        self.evnCtlr = None
        self.buildCtlr = None
        self.animalCtlr = None
        self.jobCtlr = None
        self.surface = None

        self.roles = {}
        self.role_textures = {}

    def __getitem__(self, id_):
        return self.roles[id_]

    def setUpCtlr(self, evnCtlr, animalCtlr, buildCtlr, UICtlr, jobCtlr):
        self.evnCtlr = evnCtlr
        self.animalCtlr = animalCtlr
        self.buildCtlr = buildCtlr
        self.UICtlr = UICtlr
        self.jobCtlr = jobCtlr

    def change_surface(self, surface):
        self.surface = surface

    def new_work(self, role_id, type_, work_args):
        role = self.roles[role_id]
        work = role.working
        if work != None:
            if work.type == WORK.BRING_ANIMAL:
                animal = self.animalCtlr.animals[work.args["animal"]]
                animal.tamed = False

        role.working = Working(type_, role.location, work_args)

    def add_item(self, role_id, type_, count):
        return self.roles[role_id].inventory.add(type_, count)

    def set_item_forced(self, role_id, item_index, forced):
        self.roles[role_id].inventory.set_item_forced(item_index, forced)

    def check_item_forced(self, role_id, item_index):
        return self.roles[role_id].inventory.check_item_forced(item_index)

    def clear_item_index(self, role_id, item_index):
        return self.roles[role_id].inventory.clear_item_index(item_index)

    def clear_all_item(self, role_id, forced=True):
        return self.roles[role_id].inventory.clear_all_item(forced)

    def set_all_item_forced(self, role_id, forced=True):
        for slot in self.roles[role_id].inventory.slots:
            if slot == None:
                continue

            slot.forced = forced

    def click(self, x, y, viewX, viewY):
        blk_sz = self.screen.block_size
        for role in self.roles.values():
            if x < (role.x - viewX) * blk_sz:
                continue
            if x > (role.x - viewX) * blk_sz + blk_sz:
                continue

            if y < (role.y - viewY) * blk_sz:
                continue
            if y > (role.y - viewY) * blk_sz + blk_sz:
                continue
            return role.id
        return False

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
            id_ = role_info[0]
            x, y = role_info[1].split(",")
            x, y = int(x), int(y)
            location = int(role_info[2])
            working_info = role_info[3]
            inventory_info = role_info[4]

            inventory = Inventory.parse(inventory_info)

            # working = Working()
            # working.parse(working_info)

            self.roles[id_] = Role(id_, x, y, location, None, inventory)

    def tick_load(self, tick_interval):
        for role in self.roles.values():
            if role.working != None:
                if role.working.type == WORK.CHOP:
                    right_position = role.move(role.working["wood"], tick_interval)

                    if right_position:
                        if int(role.working.progress) == role.working.progress_need:
                            self.evnCtlr.change_map(role.location, role.working["wood"], AIR)

                            role.inventory.add("wood", randint(10, 30))
                            role.working = None
                        else:
                            role.working.progress += tick_interval

                elif role.working.type == WORK.BUILD:
                    blueprint = self.buildCtlr.blueprints[role.working["id"]]
                    right_position = role.move(blueprint.hitbox_lt, tick_interval)
                    resource_need = self.build_info.resource_need[blueprint.type]

                    if right_position:
                        if not blueprint.reach_resrc_need(resource_need):
                            resource_add = blueprint.put_resrc(
                                role.inventory,
                                self.build_info.resource_need[blueprint.type],
                                )

                            for r, c in resource_add.items():
                                role.inventory.take(r, c)

                        if blueprint.reach_resrc_need(resource_need):
                            role.working.progress += tick_interval
                            if role.working.progress >= self.build_info.build_time[blueprint.type]:
                                self.buildCtlr.finish_blueprint(id(blueprint))
                                role.working = None
                        else:
                            role.working = None

                elif role.working.type == WORK.OPEN_STORAGE:
                    building = self.buildCtlr.buildings[role.working["id"]]
                    right_position = role.move(building.hitbox_lt, tick_interval)

                    if right_position:
                        self.UICtlr.open_building_ui(
                            role.working["id"], role.id)
                        role.working = None

                elif role.working.type == WORK.CLEAR_ITEM:
                    storage = self.buildCtlr.buildings[role.working["storage"]]
                    right_position = role.move(storage.hitbox_lt, tick_interval)

                    if right_position:
                        role.inventory.transfer(storage.inventory, forced=True)
                        role.working = None

                elif role.working.type == WORK.CLEAR_BUILD_INV:
                    building = self.buildCtlr.buildings[role.working["build"]]
                    right_position = role.move(building.hitbox_lt, tick_interval)
                    next_ = role.working["next"]

                    if right_position:
                        building.inventory.transfer(role.inventory)
                        self.new_work(role.id, next_["type"], next_)

                elif role.working.type == WORK.CAPTURE_ANIMAL:
                    animal = self.animalCtlr.animals[role.working["animal"]]
                    right_position = role.move((animal.x, animal.y), tick_interval)

                    if right_position:
                        animal.tamed = True
                        self.new_work(role.id, WORK.BRING_ANIMAL, role.working.args)

                elif role.working.type == WORK.BRING_ANIMAL:
                    farm = self.buildCtlr.buildings[role.working["farm"]]
                    animal = self.animalCtlr.animals[role.working["animal"]]
                    right_position = role.move(farm.hitbox_lt, tick_interval)
                    animal.x = role.x
                    animal.y = role.y

                    if right_position:
                        if animal.type not in farm.animals:
                            farm.animals[animal.type] = 0
                        farm.animals[animal.type] += 1

                        self.animalCtlr.animals.pop(role.working["animal"])
                        role.working = None

                elif role.working.type == WORK.GO_MINE:
                    mine = self.buildCtlr.buildings[role.working["mine"]]
                    right_position = role.move(mine.hitbox_lt, tick_interval)

                    if right_position:
                        if int(mine.depth) < mine.max_depth:
                            mine.depth += 10 * tick_interval
                        else:
                            role.location = self.evnCtlr.dig_down(mine)
                            role.working = None

                elif role.working.type == WORK.GO_SURFACE:
                    right_position = role.move(role.working["exit"], tick_interval)

                    if right_position:
                        role.location = role.working["layer"]
                        role.working = None

                elif role.working.type == WORK.MINE_BLOCK:
                    right_position = role.move(role.working["id"], tick_interval)

                    if right_position:
                        if int(role.working.progress) == role.working.progress_need:
                            block_type = self.evnCtlr.change_map(role.location,
                                role.working["id"],
                                AIR)

                            if block_type == ROCK:
                                role.inventory.add("pebble", randint(10, 30))
                            elif block_type == COAL:
                                role.inventory.add("coal", randint(8, 12))
                            elif block_type == COPPER:
                                role.inventory.add("copper_ore", randint(5, 7))
                            elif block_type == IRON:
                                role.inventory.add("iron_ore", randint(5, 7))
                            elif block_type == GOLD:
                                role.inventory.add("gold_ore", randint(5, 7))
                            role.working = None
                        else:
                            role.working.progress += tick_interval

                elif role.working.type == WORK.DO_BUILDING_JOB:
                    building = self.buildCtlr[role.working["building"]]
                    right_position = role.move(building.hitbox_lt, tick_interval)

                    if right_position:
                        if int(role.working.progress) == role.working.progress_need:
                            work = role.working["work"]
                            role.inventory.add(work["product"], work["amount"])
                            building.jobs.pop(role.working["work_index"])

                            building.doing = None
                            role.working = None
                        else:
                            role.working.progress += tick_interval
                            building.doing = True
            elif len(self.jobCtlr.queue) > 0:
                role.working = self.jobCtlr.get(role.location)

    def render(self, viewX, viewY):
        blk_sz = self.screen.block_size

        for role in self.roles.values():
            if role.location != self.evnCtlr.present_layer.type:
                continue
            if role.x >= viewX and role.x - viewX < self.screen.width_blocks:
                if role.y >= viewY and role.y - viewY < self.screen.height_blocks:
                    x = (role.x - viewX) * blk_sz
                    y = (role.y - viewY) * blk_sz

                    if blk_sz not in self.role_textures:
                        self.role_textures[blk_sz] = pygame.transform.scale(
                            self.images["texture/role.png"],
                            (blk_sz, blk_sz),
                            )
                    self.surface.blit(self.role_textures[blk_sz], (x, y))
