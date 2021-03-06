import pygame
import os
import math
import re
import json

from random import randint

from color import clr
from pygame_extendtion import *
from role import WORK
from building import BluePrint, F_UP, F_DOWN, F_LEFT, F_RIGHT
from animal import COW, SHEEP, CHICKEN
from enviroment import AIR, ROCK, TREE, COAL, COPPER, IRON, GOLD
from enviroment import GROUND, UNDERGROUND, EXIT

# object type
ROLE = "role"
BUILDING = "building"
INV_ITEM_SIZE = 35
INV_WIDTH = INV_ITEM_SIZE * 5 + 60
INV_HEIGHT = INV_ITEM_SIZE * 2 + 30

# select event
CLOSE_INFO_UI = "cls_info_ui"
MENU_UI = "menu_ui"
BUILD_UI = "build_new_building_ui"
ITEM_SELECT_UI = "item_select_ui"

# full ui event
CLOSE_FULL_UI = "close_full_ui"

# storage event
ASIGN_GO_STORAGE = "asign_role_to_storage"
FORCE_ITEM = "force_item"
UNFORCE_ITEM = "unforce_item"
CLEAR_ITEM = "clear_item"
CLEAR_ALL_ITEM = "clear_all_item"
CLEAR_ALL_UNFORCE_ITEM = "clear_all_unforce_item"
FORCE_ALL_ITEM = "force_all_item"
UNFORCE_ALL_ITEM = "unforce_all_item"

CHOP_TREE = "chop_tree"

# building event
NEW_BUILDING = "new_building"
ASIGN_BUILD = "asign_role_to_build"

# farm event
ASIGN_GO_FARM = "asign_role_to_farm"
TARGET_CAPTURE = "set_target_to_capture_animal"
TRANS_FARM_STORAGE = "asign_transfer_farm_storage"

# mine event
ASIGN_GO_MINE = "asign_role_to_mine"
MINE_BLOCK = "mine_block"
BACK_SURFACE = "back_to_surface"

# smelter event
SHOW_SMELTER_JOB = "show_smelter_jobs"


# forge event
SHOW_FORGE_JOB = "show_forge_jobs"

ASIGN_JOB = "asign_job"
ADD_JOB = "add_job"

# building rotate
face_up = lambda p: (p[1], -p[0])
face_down = lambda p: (-p[1], p[0])
face_left = lambda p: (-p[0], -p[1])
face_right = lambda p: (p[0], p[1])

class ItemInfo:
    def __init__(self):
        self.items = {}

    def load(self, file, images):
        path = os.getcwd()
        with open(os.path.join(path, file)) as file:
            read = file.read()
        self.items = json.loads(read)

        ITEM_TEXTURE_DIR = os.path.join("texture", "item")
        for i, item in self.items.items():
            file = os.path.join(ITEM_TEXTURE_DIR, item["src"])
            if os.path.isfile(file):
                self.items[i]["src"] = images[file]

            self.__setattr__(item["name"].upper(), i)

class BuildingPlaceDown:
    def __init__(self, type_, width, height):
        self.type = type_
        self.width = width
        self.height = height

        self.rotate = face_right

        self.boxes = []
        for i in range(height):
            for e in range(width):
                self.boxes.append((e, i))

    def rotate_building(self, direction):
        if direction == "L":
            if self.rotate == face_up:
                self.rotate = face_right
            elif self.rotate == face_right:
                self.rotate = face_down
            elif self.rotate == face_down:
                self.rotate = face_left
            elif self.rotate == face_left:
                self.rotate = face_up
        else:
            if self.rotate == face_up:
                self.rotate = face_left
            elif self.rotate == face_left:
                self.rotate = face_down
            elif self.rotate == face_down:
                self.rotate = face_right
            elif self.rotate == face_right:
                self.rotate = face_up

    def get_boxes(self):
        boxes_draw = []
        for box in self.boxes:
            boxes_draw.append(self.rotate(box))
        return boxes_draw

class Button:
    def __init__(self, pos, size, floting=False, event=None, args=None,
        text=None, border_clr=None, bg_clr=clr.black_ui_bg):
        self.x, self.y = pos
        self.width, self.height = size
        self.floting = floting
        self.text = text

        self.border_clr = border_clr
        self.bg_clr = bg_clr

        self.event = event
        if args != None:
            self.args = args
        else:
            self.args = {}

    def __repr__(self):
        return f"{self.floting} {self.x},{self.y} {self.event}"

    def __getitem__(self, key):
        return self.args[key]

    def click(self, pos, blk_sz, viewX, viewY):
        m_x, m_y = pos
        x = self.x
        y = self.y
        width = self.width
        height = self.height
        if self.floting:
            x = (self.x - viewX) * blk_sz
            y = (self.y - viewY + 1) * blk_sz

            if self.floting:
                width *= blk_sz
                height *= blk_sz
        else:
            pass

        if m_x > x and m_x < x + width:
            if m_y > y and m_y < y + height:
                return True
        return False

    def render(self, surface, viewX, viewY, blk_sz):
        x = self.x
        y = self.y
        width = self.width
        height = self.height
        if self.floting:
            x = (x - viewX) * blk_sz
            y = (y - viewY + 1) * blk_sz
            width *= blk_sz
            height *= blk_sz

        if self.bg_clr:
            pygame.draw.rect(surface, self.bg_clr, (x, y, width, height))

        if self.border_clr:
            pygame.draw.rect(surface, self.border_clr, (x, y, width, height), 2)

        if self.text:
            surface.blit(self.text, (x, y))

class ButtonGroup:
    def __init__(self):
        self.buttons = {}
        self.event_to_button = {}

    def __iter__(self):
        for elem in self.buttons.values():
            yield elem

    def append(self, button):
        id_ = self.new_id()
        self.buttons[id_] = button
        if button.event != None:
            if button.event not in self.event_to_button:
                self.event_to_button[button.event] = []
            self.event_to_button[button.event].append(id_)

    def clear_all(self):
        self.buttons.clear()
        self.event_to_button.clear()

    def event_clear(self, event):
        if isinstance(event, str):
            if event in self.event_to_button:
                for button_id in self.event_to_button[event]:
                    try:
                        self.buttons.pop(button_id)
                    except:
                        pass
        else:
            for e in event:
                if e in self.event_to_button:
                    for button_id in self.event_to_button[e]:
                        try:
                            self.buttons.pop(button_id)
                        except:
                            pass

    def del_btn_id(self, button_id):
        try:
            self.buttons.pop(button_id)
        except:
            pass

    def new_id(self):
        id_ = randint(1,999)
        btn_keys = self.buttons.keys()
        while id_ in btn_keys:
            id_ = randint(1,999)
        return id_

class UIController:
    def __init__(self, screen_info, build_info, items_info):
        self.screen = screen_info
        self.build_info = build_info

        self.surface = None
        self.roleCtlr = None
        self.envCtlr = None
        self.buildCtlr = None
        self.jobCtlr = None

        self.font = None
        self.close_icon = None

        self.left_selected = None
        self.right_selected = None
        self.mouse_pos = (0, 0)
        self.buttons = ButtonGroup()
        self.right_buttons = ButtonGroup()

        self.items_info = items_info

        self.full_ui = None

    def change_surface(self, surface):
        self.surface = surface

        self.font = Font()

        self.storage_ico = pygame.transform.scale(
            pygame.image.load("texture/building/icon/storage.png"), (30, 30)
            )

    def setUpCtlr(self, envCtlr, roleCtlr, buildCtlr, animalCtlr, jobCtlr):
        self.envCtlr = envCtlr
        self.roleCtlr = roleCtlr
        self.buildCtlr = buildCtlr
        self.animalCtlr = animalCtlr
        self.jobCtlr = jobCtlr

    def press(self, key):
        if self.left_selected != None:
            if self.left_selected[0] == NEW_BUILDING:
                if key == pygame.K_q:
                    self.left_selected[1].rotate_building("L")
                elif key == pygame.K_e:
                    self.left_selected[1].rotate_building("R")

    def clear_buttons(self):
        self.buttons.clear_all()
        self.right_buttons.clear_all()

    def mouse_motion(self, pos):
        self.mouse_pos = pos

    def detect_buttons(self, viewX, viewY):
        blk_sz = self.screen.block_size

        for btn in self.buttons:
            if btn.click(self.mouse_pos, blk_sz, viewX, viewY):
                if btn.event == CLOSE_INFO_UI:
                    try:
                        self.buttons.event_clear(btn.args["button_close"])
                        self.right_buttons.event_clear(btn.args["button_close"])
                    except:
                        pass

                    self.buttons.event_clear(CLOSE_INFO_UI)
                    self.left_selected = None

                elif btn.event == CLOSE_FULL_UI:
                    self.full_ui = None
                    self.left_selected = None
                    self.right_selected = None
                    self.buttons.clear_all()
                    self.right_buttons.clear_all()

                elif btn.event == FORCE_ITEM:
                    self.roleCtlr.set_item_forced(btn["role"],
                        btn["item_index"], True)

                    self.buttons.event_clear((FORCE_ITEM, CLEAR_ITEM))

                elif btn.event == UNFORCE_ITEM:
                    self.roleCtlr.set_item_forced(btn["role"],
                        btn["item_index"], False)

                    self.buttons.event_clear((UNFORCE_ITEM, CLEAR_ITEM))

                elif btn.event == CLEAR_ITEM:
                    type_, count = self.roleCtlr.clear_item_index(btn["role"],
                        btn["item_index"])

                    self.buttons.event_clear((UNFORCE_ITEM, FORCE_ITEM, CLEAR_ITEM))

                    self.buildCtlr[btn["item_into"]].inventory.add(type_, count)

                elif (btn.event == CLEAR_ALL_ITEM) or (btn.event == CLEAR_ALL_UNFORCE_ITEM):
                    role_id = btn["role"]
                    if btn.event == CLEAR_ALL_ITEM:
                        counts = self.roleCtlr.clear_all_item(role_id)
                    else:
                        counts = self.roleCtlr.clear_all_item(role_id, forced=False)

                    building = self.buildCtlr[btn["item_into"]]
                    for type_, count in counts.items():
                        building.inventory.add(type_, count)

                elif (btn.event == FORCE_ALL_ITEM) or (btn.event == UNFORCE_ALL_ITEM):
                    role_id = btn["role"]
                    if btn.event == FORCE_ALL_ITEM:
                        counts = self.roleCtlr.set_all_item_forced(role_id)
                    else:
                        counts = self.roleCtlr.set_all_item_forced(role_id, forced=False)

                elif btn.event == TARGET_CAPTURE:
                    self.left_selected = (TARGET_CAPTURE, btn["farm"])

                    self.full_ui = None
                    self.buttons.clear_all()
                    self.right_buttons.clear_all()

                elif btn.event == TRANS_FARM_STORAGE:
                    build = self.buildCtlr[btn["build"]]

                    if "inventory" not in dir(build):
                        return True

                    if build.inventory.slots.count(None) != build.inventory.limit:
                        self.jobCtlr.put(WORK.CLEAR_BUILD_INV,
                            self.envCtlr.present_layer.type, btn.args)

                        self.buttons.clear_all()
                        self.right_buttons.clear_all()
                        self.full_ui = None

                elif btn.event == SHOW_SMELTER_JOB:
                    self.buttons.clear_all()

                    self.open_building_ui(
                        btn["smelter"],
                        None)

                elif btn.event == ADD_JOB:
                    building = self.buildCtlr[btn["building"]]
                    building.jobs.append(btn["work"])

                elif btn.event == SHOW_FORGE_JOB:
                    self.buttons.clear_all()

                    self.open_building_ui(
                        btn["forge"],
                        None)

                return True

        for btn in self.right_buttons:
            if btn.click(self.mouse_pos, blk_sz, viewX, viewY):
                if btn.event == CHOP_TREE:
                    self.jobCtlr.put(WORK.CHOP,self.envCtlr.present_layer.type,
                        btn.args)

                    self.right_buttons.clear_all()
                    self.right_selected = None

                elif btn.event == ASIGN_BUILD:
                    blueprint = self.buildCtlr.blueprints[btn["id"]]
                    role = self.roleCtlr.roles[btn["role"]]

                    resource_need = self.build_info.resource_need[blueprint.type]

                    has_resrc = False
                    for resrc in resource_need:
                        if role.inventory.count_item(resrc) > 0:
                            has_resrc = True
                            break

                    if has_resrc or blueprint.reach_resrc_need(resource_need):
                        self.roleCtlr.new_work(btn["role"], WORK.BUILD, btn.args)

                    self.right_buttons.clear_all()
                    self.right_selected = None

                elif btn.event == ASIGN_GO_STORAGE:
                    self.roleCtlr.new_work(btn["role"], WORK.OPEN_STORAGE, btn.args)

                    self.right_buttons.clear_all()
                    self.right_selected = None

                elif btn.event == ITEM_SELECT_UI:
                    btn_event = UNFORCE_ITEM
                    btn_txt = "Unforce Item"
                    forced = self.roleCtlr.check_item_forced(btn["role"],
                        btn["item_index"])
                    if forced == None:
                        return True
                    elif forced == False:
                        btn_txt = "Force Item"
                        btn_event = FORCE_ITEM

                    self.buttons.append(Button(
                            (btn.x, btn.y + INV_ITEM_SIZE),
                            (100, 20),
                            event=btn_event,
                            border_clr=clr.white,
                            args=btn.args,
                            text=self.font.get_16_text(btn_txt, clr.white)
                        ))

                    self.buttons.append(Button(
                            (btn.x, btn.y + INV_ITEM_SIZE + 20),
                            (100, 20),
                            event=CLEAR_ITEM,
                            border_clr=clr.white,
                            args=btn.args,
                            text=self.font.get_16_text("Clear Item", clr.white)
                        ))

                elif btn.event == BACK_SURFACE:
                    self.roleCtlr.new_work(btn["role"], WORK.GO_SURFACE, btn.args)

                    self.right_buttons.clear_all()
                    self.right_selected = None

                elif btn.event == ASIGN_JOB:
                    # check role resource
                    role = self.roleCtlr[btn["role"]]
                    if role.inventory.check_empty_slot() == 0:
                        self.right_buttons.clear_all()
                        self.right_selected = None
                        return

                    resource_need = btn["work"]["need"]
                    for type_, count in resource_need.items():
                        if count > role.inventory.count_item(type_):
                            self.right_buttons.clear_all()
                            self.right_selected = None
                            return

                    for type_, count in resource_need.items():
                        role.inventory.take(type_, count)

                    self.roleCtlr.new_work(btn["role"], WORK.DO_BUILDING_JOB, btn.args)

                    self.buttons.clear_all()
                    self.right_buttons.clear_all()
                    self.left_selected = None

                return True
        return False

    def envir_right_click(self, x, y, viewX, viewY):
        block_clicked = self.envCtlr.click(x, y, viewX, viewY)
        if block_clicked:
            if block_clicked[0] == TREE:
                self.jobCtlr.put(WORK.CHOP, self.envCtlr.present_layer.type,
                    {"wood": block_clicked[1:]})
                return True

            elif self.envCtlr.present_layer.type == UNDERGROUND:
                if block_clicked[0] == EXIT:
                    y = block_clicked[2]
                    for i, role in self.roleCtlr.roles.items():
                        if role.location == self.envCtlr.present_layer.type:
                            self.right_buttons.append(Button(
                                (block_clicked[1], y),
                                (12, 2),
                                event=BACK_SURFACE,
                                args={
                                    "role": i,
                                    "exit": (block_clicked[1], block_clicked[2]),
                                    "layer": GROUND},
                                floting=True,
                                text=self.font.get_16_text(
                                    f"Let {i} back to surface", clr.white)
                                ))
                            y += 2
                    return True

                elif block_clicked[0] != AIR:
                    self.jobCtlr.put(WORK.MINE_BLOCK,
                        self.envCtlr.present_layer.type,
                        {"id": block_clicked[1:]})

                    return True
        return False

    def building_left_click(self, x, y, viewX, viewY):
        build_clicked = self.buildCtlr.click(x, y, viewX, viewY)
        if type(build_clicked).__name__ == "Building":
            building = build_clicked

            if building.type == self.build_info.MINE:
                self.left_selected = (BUILDING, id(building))

                self.buttons.append(Button(
                    pos=(0, self.screen.height - INV_HEIGHT - 30),
                    size=(24, 24),
                    event=CLOSE_INFO_UI,
                    text=self.font.get_24_text("X", clr.red),
                    bg_clr=None,
                    ))
                return True
            elif building.type == self.build_info.SMELTER:
                if building.doing != None:
                    return True

                self.left_selected = (BUILDING, id(building))
                self.buttons.clear_all()

                self.buttons.append(Button(
                    pos=(0, self.screen.height - INV_HEIGHT - 150),
                    args={
                        "button_close": (SHOW_SMELTER_JOB, )},
                    size=(24, 24),
                    event=CLOSE_INFO_UI,
                    text=self.font.get_24_text("X", clr.red),
                    bg_clr=None,
                    ))

                self.buttons.append(Button(
                    pos=(60, self.screen.height - INV_HEIGHT - 150),
                    args={
                        "smelter": id(building)},
                    size=(24, 24),
                    event=SHOW_SMELTER_JOB,
                    text=self.font.get_24_text("+", clr.yellow),
                    bg_clr=None,
                    ))
                return True

            elif building.type == self.build_info.FORGE:
                if building.doing != None:
                    return True

                self.left_selected = (BUILDING, id(building))
                self.buttons.clear_all()

                self.buttons.append(Button(
                    pos=(0, self.screen.height - INV_HEIGHT - 150),
                    args={
                        "button_close": (SHOW_FORGE_JOB, )},
                    size=(24, 24),
                    event=CLOSE_INFO_UI,
                    text=self.font.get_24_text("X", clr.red),
                    bg_clr=None,
                    ))

                self.buttons.append(Button(
                    pos=(60, self.screen.height - INV_HEIGHT - 150),
                    args={
                        "forge": id(building)},
                    size=(24, 24),
                    event=SHOW_FORGE_JOB,
                    text=self.font.get_24_text("+", clr.yellow),
                    bg_clr=None,
                    ))
                return True
        return False

    def building_right_click(self, x, y, viewX, viewY):
        build_clicked = self.buildCtlr.click(x, y, viewX, viewY)
        if type(build_clicked).__name__ == "BluePrint":
            blueprint = build_clicked

            y = blueprint.hitbox_lt[1]
            blueprint_type = self.build_info.buildings[blueprint.type]["name"]
            for role in self.roleCtlr.roles:
                self.right_buttons.append(Button(
                    (blueprint.hitbox_lt[0], y),
                    (13, 2),
                    event=ASIGN_BUILD,
                    args={
                        "role": role,
                        "id": id(blueprint)},
                    floting=True,
                    text=self.font.get_16_text(
                        f"Asign {role} to build {blueprint_type}",
                        clr.white)
                    ))
                y += 2
            return True

        elif type(build_clicked).__name__ == "Building":
            building = build_clicked

            if building.type == self.build_info.STORAGE:
                y = building.hitbox_rd[1] - 1
                for role in self.roleCtlr.roles:
                    self.right_buttons.append(Button(
                        (building.hitbox_lt[0], y),
                        (13, 2),
                        event=ASIGN_GO_STORAGE,
                        args={
                            "role": role,
                            "id": id(building)},
                        floting=True,
                        text=self.font.get_16_text(
                            f"Asign {role} to open this Storage",
                            clr.white)
                        ))
                    y += 2

            elif building.type == self.build_info.FARM:
                self.open_building_ui(id(building))

            elif building.type == self.build_info.MINE:
                self.jobCtlr.put(WORK.GO_MINE,
                    self.envCtlr.present_layer.type, {"mine": id(building)})

            return True
        return False

    def left_click(self, viewX, viewY):
        x, y = self.mouse_pos
        blk_sz = self.screen.block_size

        button_press = self.detect_buttons(viewX, viewY)
        if button_press:
            return

        if self.full_ui:
            self.buttons.event_clear([CLEAR_ITEM, FORCE_ITEM, UNFORCE_ITEM])

            if self.full_ui[0] == "Building":
                building = self.buildCtlr[self.full_ui[1]]
                if building.type == self.build_info.STORAGE:
                    storage = building

                    y_2_x = (self.screen.width - 60) // (INV_ITEM_SIZE + 10)
                    if x > 30 and y > 200:
                        slot_index = (x - 30) // (INV_ITEM_SIZE + 10)
                        col = (y - 200) // (INV_ITEM_SIZE + 10)
                        col *= y_2_x
                        slot_index += col

                        if len(storage.inventory) > slot_index:
                            slot = storage.inventory[slot_index]
                            if slot == None:
                                return

                            count = self.roleCtlr.add_item(self.full_ui[2], slot.type, slot.count)

                            if count > 0:
                                storage.inventory[slot_index].count = count
                            else:
                                storage.inventory.clear_item_index(slot_index)
            return

        # building menu button
        if x < 100:
            if y > self.screen.height - 25:
                self.left_selected = (MENU_UI, )
                return

        if self.left_selected != None:
            select_type = self.left_selected[0]
            if select_type == MENU_UI:
                icn_btn_x = 5
                icn_btn_y = self.screen.height - 70

                for i, building in self.build_info.buildings.items():
                    if not isinstance(building["icon_src"], str):

                        if x >= icn_btn_x and x < icn_btn_x + 40:
                            if y >= icn_btn_y and y < icn_btn_y + 40:
                                self.left_selected = (NEW_BUILDING,
                                    BuildingPlaceDown(i, building["width"], building["height"]))
                                return
                        icn_btn_x += 45

            elif select_type == NEW_BUILDING:
                x = (viewX + x // blk_sz)
                y = (viewY + y // blk_sz)
                overlap = self.envCtlr.present_layer.check_overlap(
                    self.left_selected[1].get_boxes(), self.mouse_pos)
                building_overlap = self.buildCtlr.check_overlap(
                    self.left_selected[1].get_boxes(), self.mouse_pos)

                if overlap or building_overlap:
                    return

                rotate = self.left_selected[1].rotate
                if rotate == face_up:
                    rotate = F_UP
                elif rotate == face_down:
                    rotate = F_DOWN
                elif rotate == face_left:
                    rotate = F_LEFT
                elif rotate == face_right:
                    rotate = F_RIGHT

                self.buildCtlr.new_blueprint(BluePrint(
                    self.left_selected[1].type,
                    (x, y),
                    rotate,
                    self.build_info
                    ))

            elif select_type == TARGET_CAPTURE:
                x = (x // blk_sz) + viewX
                y = (y // blk_sz) + viewY

                closet = None
                for i, animal in enumerate(self.animalCtlr.animals):
                    dis = count_distance(animal.x, animal.y, x, y)
                    if closet == None:
                        if dis < 1:
                            closet = (dis, i)
                    elif closet[0] > dis:
                        closet = (dis, i)

                if closet:
                    self.jobCtlr.put(WORK.CAPTURE_ANIMAL,
                        self.envCtlr.present_layer.type,
                        {"animal": closet[1], "farm": self.left_selected[1]})
                self.left_selected = None
                return

            elif self.left_selected[0] == BUILDING:
                building = self.buildCtlr[self.left_selected[1]]
                if building.type == self.build_info.SMELTER or building.type == self.build_info.FORGE:
                    if building.doing != None:
                        return

                    item_y = self.screen.height - INV_HEIGHT - 150

                    work = None
                    work_index = None
                    item_y += 30
                    for i, job in enumerate(building.jobs):
                        if 10 <= x <= 42:
                            if item_y <= y <= item_y + 32:
                                work = job
                                work_index = i
                                break

                    if work != None:
                        y = item_y + 30
                        y /= blk_sz
                        for role in self.roleCtlr.roles:
                            self.right_buttons.append(Button(
                                (1, y),
                                (12, 2),
                                event=ASIGN_JOB,
                                args={
                                    "role": role,
                                    "work": work,
                                    "work_index": work_index,
                                    "building": self.left_selected[1]},
                                floting=True,
                                text=self.font.get_16_text(
                                    f"Asign {role} to smelt {work['product']}", clr.white)
                                ))
                            y += 2
                        return True

                elif building.type == self.build_info.FORGE:
                    return True

        # detect role is clicked
        role_clicked = self.roleCtlr.click(x, y, viewX, viewY)
        if role_clicked:
            self.left_selected = (ROLE, role_clicked)

            self.buttons.append(Button(
                pos=(0, self.screen.height - INV_HEIGHT - 30),
                size=(24, 24),
                event=CLOSE_INFO_UI,
                text=self.font.get_24_text("X", clr.red),
                bg_clr=None,
                ))
            return

        # detect build is clicked
        breaked = self.building_left_click(x, y, viewX, viewY)
        if breaked:
            return

        self.buttons.clear_all()
        self.left_selected = None

    def right_click(self, viewX, viewY):
        x, y = self.mouse_pos
        blk_sz = self.screen.block_size

        # if self.full_ui:
        #     button_press = self.detect_buttons(viewX, viewY)
        #     return

        # right click to chop tree
        breaked = self.envir_right_click(x, y, viewX, viewY)
        if breaked:
            return
        
        # check blueprint or building is clicked
        breaked = self.building_right_click(x, y, viewX, viewY)
        if breaked:
            return

        self.right_buttons.clear_all()
        self.right_selected = None

    def draw_button(self, viewX, viewY):
        blk_sz = self.screen.block_size
        for btn in self.buttons:
            btn.render(self.surface, viewX, viewY, blk_sz)

        for btn in self.right_buttons:
            btn.render(self.surface, viewX, viewY, blk_sz)

    def disp_role_UI(self, role):
        pygame.draw.rect(self.surface,
            clr.black_ui_bg,
            (0, self.screen.height - INV_HEIGHT - 30,
            INV_WIDTH, INV_HEIGHT),
            )

        x = 10
        y = self.screen.height - INV_HEIGHT - 20
        for item in role.inventory.slots:

            frame_color = clr.white
            if item != None:
                self.surface.blit(self.items_info.items[item.type]["src"], (x, y))

                self.surface.blit(self.font.get_16_text(str(item.count), clr.white),
                    (x + 5, y + INV_ITEM_SIZE - 12))

                if item.forced:
                    frame_color = clr.red
            
            pygame.draw.rect(self.surface,
                frame_color,
                (x, y, INV_ITEM_SIZE, INV_ITEM_SIZE),
                2)

            x += INV_ITEM_SIZE + 10
            if x >= INV_WIDTH:
                y += INV_ITEM_SIZE + 10
                x = 10

    def disp_build_info_UI(self, building):
        if building.type == self.build_info.MINE:
            pygame.draw.rect(self.surface,
                clr.black_ui_bg,
                (0, self.screen.height - INV_HEIGHT - 30,
                INV_WIDTH, INV_HEIGHT),
                )

            str_ = f"{int(building.depth)} / {building.max_depth}"
            self.surface.blit(self.font.get_24_text(str_, clr.white),
                (50, self.screen.height - 100))

        elif building.type == self.build_info.SMELTER or building.type == self.build_info.FORGE:
            y = self.screen.height - INV_HEIGHT - 150
            pygame.draw.rect(self.surface,
                clr.black_ui_bg,
                (0, self.screen.height - INV_HEIGHT - 150,
                80, INV_HEIGHT + 120),
                )

            y += 30
            for job in building.jobs:
                self.surface.blit(self.items_info.items[job["product"]]["src"],
                    (10, y))
                y += 30

    def open_building_ui(self, building_id, role_id=None):
        self.full_ui = ("Building", building_id, role_id)
        self.right_buttons.clear_all()

        building = self.buildCtlr[building_id]

        self.buttons.append(Button(
            pos=(20, 20),
            size=(24, 24),
            text=self.font.get_24_text("X", clr.red),
            bg_clr=None,
            event=CLOSE_FULL_UI
            ))

        if building.type == self.build_info.STORAGE:
            x = 30
            y = 60

            role = self.roleCtlr.roles[role_id]
            for i, item in enumerate(role.inventory.slots):
                self.right_buttons.append(Button(
                    pos=(x, y),
                    size=(INV_ITEM_SIZE, INV_ITEM_SIZE),
                    floting=False,
                    bg_clr=None,
                    event=ITEM_SELECT_UI,
                    args={"item_index": i,
                        "role": role_id,
                        "item_into": building_id}
                    ))
                x += INV_ITEM_SIZE + 10

            args = {"role": role_id, "item_into": building_id}

            self.buttons.append(Button(
                pos=(30, 140),
                size=(130, 22),
                floting=False,
                bg_clr=clr.blue,
                border_clr=clr.white,
                text=self.font.get_20_text("Clear All Item", clr.white),
                event=CLEAR_ALL_ITEM,
                args=args
                ))

            self.buttons.append(Button(
                pos=(170, 140),
                size=(190, 22),
                floting=False,
                bg_clr=clr.blue,
                border_clr=clr.white,
                text=self.font.get_20_text("Clear Unforced Item", clr.white),
                event=CLEAR_ALL_UNFORCE_ITEM,
                args=args
                ))

            self.buttons.append(Button(
                pos=(30, 170),
                size=(130, 22),
                floting=False,
                bg_clr=clr.orange,
                border_clr=clr.white,
                text=self.font.get_20_text("Force All Item", clr.white),
                event=FORCE_ALL_ITEM,
                args=args
                ))

            self.buttons.append(Button(
                pos=(170, 170),
                size=(160, 22),
                floting=False,
                bg_clr=clr.green,
                border_clr=clr.white,
                text=self.font.get_20_text("UnForce All Item", clr.white),
                event=UNFORCE_ALL_ITEM,
                args=args
                ))

        elif building.type == self.build_info.FARM:
            args = {
                "build": building_id,
                "next": {
                    "type": WORK.CLEAR_ITEM,
                    "storage": None,
                    }
            }
            self.buttons.append(Button(
                pos=(self.screen.width - 80, 40),
                size=(40, 40),
                event=TARGET_CAPTURE,
                bg_clr=clr.red,
                args={"farm": building_id}
                ))

            x = 40
            y = 90
            for id_, building in self.buildCtlr.buildings.items():
                if building.type == self.build_info.STORAGE:
                    args["next"]["storage"] = id_
                    self.buttons.append(Button(
                        pos=(x, y),
                        size=(420, 25),
                        text=self.font.get_24_text(f"Take all the resource to Storage {id_}", clr.white),
                        border_clr=clr.white,
                        event=TRANS_FARM_STORAGE,
                        args=args
                        ))
                    y += 30

        elif building.type == self.build_info.SMELTER or building.type == self.build_info.FORGE:
            if building.type == self.build_info.SMELTER:
                works_info = self.build_info.buildings[self.build_info.SMELTER]["works"]
            else:
                works_info = self.build_info.buildings[self.build_info.FORGE]["works"]

            x = 80
            y = 50
            for work in works_info:
                self.buttons.append(Button(
                    pos=(x, y),
                    size=(30, 30),
                    text=self.font.get_28_text(f"+", clr.white),
                    border_clr=clr.white,
                    event=ADD_JOB,
                    args={
                        "building":building_id,
                        "work": work}
                    ))
                y += 50

    def render_full_ui(self):
        pygame.draw.rect(self.surface, clr.black_ui_bg,
            (20, 20, self.screen.width - 40, self.screen.height - 40))

        if self.full_ui[0] == "Building":
            building = self.buildCtlr[self.full_ui[1]]

            if building.type == self.build_info.STORAGE:
                role = self.roleCtlr[self.full_ui[2]]
                x = 30
                y = 60
                for item in role.inventory.slots:

                    frame_color = clr.white
                    if item != None:
                        self.surface.blit(self.items_info.items[item.type]["src"], (x, y))

                        self.surface.blit(self.font.get_16_text(str(item.count), clr.white),
                            (x + 5, y + INV_ITEM_SIZE - 12))

                        if item.forced:
                            frame_color = clr.red
                    
                    pygame.draw.rect(self.surface,
                        frame_color,
                        (x, y, INV_ITEM_SIZE, INV_ITEM_SIZE),
                        2)

                    x += INV_ITEM_SIZE + 10

                x = 30
                y = 200
                storage = building
                for item in storage.inventory.slots:
                    frame_color = clr.white
                    if item != None:
                        self.surface.blit(self.items_info.items[item.type]["src"], (x, y))

                        self.surface.blit(self.font.get_16_text(str(item.count), clr.white),
                            (x + 5, y + INV_ITEM_SIZE - 12))

                        if item.forced:
                            frame_color = clr.red
                    
                    pygame.draw.rect(self.surface,
                        frame_color,
                        (x, y, INV_ITEM_SIZE, INV_ITEM_SIZE),
                        2)

                    if x + INV_ITEM_SIZE + 10 > (self.screen.width - 60):
                        x = 30
                        y += INV_ITEM_SIZE + 10
                    else:
                        x += INV_ITEM_SIZE + 10

            elif building.type == self.build_info.FARM:
                farm = building

                x, y = 40, 40
                for item in farm.inventory.slots:
                    frame_color = clr.white
                    if item != None:
                        self.surface.blit(self.items_info.items[item.type]["src"], (x, y))

                        self.surface.blit(self.font.get_16_text(str(item.count), clr.white),
                            (x + 5, y + INV_ITEM_SIZE - 12))

                        if item.forced:
                            frame_color = clr.red
                    
                    pygame.draw.rect(self.surface,
                        frame_color,
                        (x, y, INV_ITEM_SIZE, INV_ITEM_SIZE),
                        2)

                    if x + INV_ITEM_SIZE + 10 > (self.screen.width - 60):
                        x = 30
                        y += INV_ITEM_SIZE + 10
                    else:
                        x += INV_ITEM_SIZE + 10

            elif building.type == self.build_info.SMELTER or building.type == self.build_info.FORGE:
                if building.type == self.build_info.SMELTER:
                    works_info = self.build_info.buildings[self.build_info.SMELTER]["works"]
                else:
                    works_info = self.build_info.buildings[self.build_info.FORGE]["works"]

                y = 50
                for work in works_info:
                    self.surface.blit(self.items_info.items[work["product"]]["src"],
                        (30, y))

                    self.surface.blit(self.font.get_16_text(str(work["amount"]), clr.white),
                        (60, y + 30))

                    x = 120
                    for type_, num in work["need"].items():
                        self.surface.blit(self.items_info.items[type_]["src"],
                            (x, y))

                        self.surface.blit(self.font.get_16_text(str(num), clr.white),
                            (x + 30, y + 30))
                        x += 50
                    y += 50

    def render(self, viewX, viewY):
        blk_sz = self.screen.block_size
        if self.full_ui:
            self.render_full_ui()
            self.draw_button(viewX, viewY)

        else:
            pygame.draw.rect(self.surface, clr.black_ui_bg,
                (0, self.screen.height - 25, 100, 25))
            self.surface.blit(self.font.get_24_text("Menu", clr.white),
                (20, self.screen.height - 23))

            if self.left_selected != None:
                select_type = self.left_selected[0]

                if select_type == ROLE:
                    role = self.roleCtlr.roles[self.left_selected[1]]

                    x = (role.x - viewX) * blk_sz
                    y = (role.y - viewY) * blk_sz

                    pygame.draw.rect(self.surface, clr.white,
                        (x, y, blk_sz, blk_sz), 2)

                    self.disp_role_UI(role)

                elif select_type == BUILDING:
                    building = self.buildCtlr[self.left_selected[1]]

                    x = (building.hitbox_lt[0] - viewX) * blk_sz
                    y = (building.hitbox_lt[1] - viewY) * blk_sz
                    width = building.width * blk_sz
                    height = building.height * blk_sz

                    pygame.draw.rect(self.surface, clr.white,
                        (x, y, width, height), 2)

                    self.disp_build_info_UI(building)

                elif select_type == MENU_UI:
                    x = 5
                    y = self.screen.height - 70

                    for building in self.build_info.buildings.values():
                        pygame.draw.rect(self.surface, clr.black_ui_bg, (x, y, 40, 40))

                        if not isinstance(building["icon_src"], str):
                            self.surface.blit(building["icon_src"], (x + 5, y + 5))
                            x += 45

                elif select_type == NEW_BUILDING:
                    boxes = self.left_selected[1].get_boxes()
                    overlap = self.envCtlr.present_layer.check_overlap(boxes, self.mouse_pos)
                    building_overlap = self.buildCtlr.check_overlap(boxes, self.mouse_pos)
                    if overlap or building_overlap:
                        if blk_sz not in self.build_info.ovrlp_bd_boxes:
                            self.build_info.ovrlp_bd_boxes[blk_sz] = pygame.transform.scale(
                                self.build_info.ovrlp_bd_box_src,
                                (blk_sz, blk_sz),
                                )

                        for box in boxes:
                            x = (box[0] + self.mouse_pos[0] // blk_sz) * blk_sz
                            y = (box[1] + self.mouse_pos[1] // blk_sz) * blk_sz
                            self.surface.blit(self.build_info.ovrlp_bd_boxes[blk_sz], (x, y))
                    else:
                        if blk_sz not in self.build_info.bd_boxes:
                            self.build_info.bd_boxes[blk_sz] = pygame.transform.scale(
                                self.build_info.bd_box_src,
                                (blk_sz, blk_sz),
                                )

                        for box in boxes:
                            x = (box[0] + self.mouse_pos[0] // blk_sz) * blk_sz
                            y = (box[1] + self.mouse_pos[1] // blk_sz) * blk_sz
                            self.surface.blit(self.build_info.bd_boxes[blk_sz], (x, y))

                elif select_type == TARGET_CAPTURE:
                    x, y = self.mouse_pos
                    x = (x // blk_sz) + viewX
                    y = (y // blk_sz) + viewY

                    closet = None
                    for i, animal in enumerate(self.animalCtlr.animals):
                        if animal.tamed == True:
                            continue

                        dis = count_distance(animal.x, animal.y, x, y)
                        if closet == None:
                            if dis < 1:
                                closet = (dis, i)
                        elif closet[0] > dis:
                            closet = (dis, i)

                    x, y = self.mouse_pos
                    x = (x // blk_sz) * blk_sz
                    y = (y // blk_sz) * blk_sz

                    pygame.draw.rect(self.surface, clr.red,
                        (x, y, blk_sz, blk_sz), 5)

                    if closet != None:
                        animal = self.animalCtlr.animals[closet[1]]

                        pygame.draw.rect(self.surface, clr.red,
                            ((animal.x - viewX) * blk_sz,
                                (animal.y - viewY) * blk_sz
                                , blk_sz, blk_sz), 5)


            self.draw_button(viewX, viewY)
