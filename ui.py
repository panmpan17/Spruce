import pygame
import os
import math
from color import clr

from pygame_extendtion import *
from role import WORK
from building import BluePrint, F_UP, F_DOWN, F_LEFT, F_RIGHT

import json

# block type
WOOD = "2"

# object type
ROLE = "role"
INV_ITEM_SIZE = 35
INV_WIDTH = INV_ITEM_SIZE * 5 + 60
INV_HEIGHT = INV_ITEM_SIZE * 2 + 30

# button event
CLOSE_ROLE_UI = "cls_role_ui"
MENU_UI = "menu_ui"
CHOP_TREE_UI = "chop_tree_ui"
BUILD_UI = "build_new_building_ui"
REACT_STORAGE_UI = "role_react_with_storage"
ITEM_SELECT_UI = "item_select_ui"
FORCE_ITEM = "force_item"
UNFORCE_ITEM = "unforce_item"

CHOP_TREE = "chop_tree"
NEW_BUILDING = "new_building"
ASIGN_BUILD = "asign_role_to_build"
ASIGN_GO_STORAGE = "asign_role_to_go_storage"


# building rotate
face_up = lambda p: (p[1], -p[0])
face_down = lambda p: (-p[1], p[0])
face_left = lambda p: (-p[0], -p[1])
face_right = lambda p: (p[0], p[1])

class ItemInfo:
    def __init__(self):
        self.items = {}

    def load(self, file):
        path = os.getcwd()
        with open(os.path.join(path, file)) as file:
            read = file.read()
        self.items = json.loads(read)

        ITEM_TEXTURE_DIR = os.path.join(path, "texture", "item")
        for i, item in self.items.items():
            file = os.path.join(ITEM_TEXTURE_DIR, item["src"])
            if os.path.isfile(file):
                self.items[i]["src"] = pygame.image.load(file)

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
        self.args = args

    def __repr__(self):
        return f"{self.floting} {self.x},{self.y} {self.event}"

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

class TextButton:
    def __init__(self, text, font, color, event=None):
        self.surface = font.render(text, 1, color)

        self.width, self.height = font.size(text)
        self.x , self.y = 0, 0

        self.event = event

    def set_pos(self, pos):
        self.x, self.y = pos

    def click(self, pos, blk_sz, viewX, viewY):
        x, y = pos
        if x > self.x and x < self.x + self.width:
            if y > self.y and y < self.y + self.height:
                return True
        return False

class UIController:
    def __init__(self, screen_info, build_info):
        self.screen = screen_info
        self.build_info = build_info

        self.surface = None
        self.roleCtlr = None
        self.envCtlr = None
        self.buildCtlr = None

        self.font = None
        self.close_icon = None

        self.left_selected = None
        self.right_selected = None
        self.mouse_pos = (0, 0)
        self.buttons = []
        self.right_buttons = []

        self.items_info = ItemInfo()

        self.full_ui = None

    def change_surface(self, surface):
        self.surface = surface

        self.font = Font()

        self.storage_ico = pygame.transform.scale(
            pygame.image.load("texture/building/icon/storage.png"), (30, 30)
            )

    def setUpCtlr(self, envCtlr, roleCtlr, buildCtlr):
        self.envCtlr = envCtlr
        self.roleCtlr = roleCtlr
        self.buildCtlr = buildCtlr

        self.items_info.load("ItemInfo.json")

    def press(self, key):
        if self.left_selected != None:
            if self.left_selected[0] == NEW_BUILDING:
                if key == pygame.K_q:
                    self.left_selected[1].rotate_building("L")
                elif key == pygame.K_e:
                    self.left_selected[1].rotate_building("R")

    def mouse_motion(self, pos):
        self.mouse_pos = pos

    def detect_buttons(self, viewX, viewY):
        blk_sz = self.screen.block_size

        for btn in self.buttons:
            if btn.click(self.mouse_pos, blk_sz, viewX, viewY):
                if btn.event == CLOSE_ROLE_UI:
                    self.buttons.remove(btn)
                    self.left_selected = None
                elif btn.event == ITEM_SELECT_UI:
                    btn_event = FORCE_ITEM
                    btn_txt = "Force Item"
                    if self.roleCtlr.check_item_forced(btn.args["role"],
                        btn.args["item_index"]):
                        btn_event = UNFORCE_ITEM

                    self.right_buttons.append(Button(
                            (btn.x, btn.y + INV_HEIGHT),
                            (100, 40),
                            event=btn_event,
                            border_clr=clr.white,
                            args=btn.args,
                            text=self.font.get_20_text(btn_txt, clr.white)
                        ))
                return True

        for btn in self.right_buttons:
            if btn.click(self.mouse_pos, blk_sz, viewX, viewY):
                if btn.event == CHOP_TREE:
                    self.roleCtlr.new_work(btn.args["role"], WORK.CHOP, btn.args["id"])

                    self.right_buttons.clear()
                    self.right_selected = None

                elif btn.event == ASIGN_BUILD:
                    blueprint = self.buildCtlr.blueprints[btn.args["id"]]
                    role = self.roleCtlr.roles[btn.args["role"]]

                    resource_need = self.build_info.resource_need[blueprint.type]

                    has_resrc = False
                    for resrc in resource_need:
                        if role.inventory.count_item(resrc) > 0:
                            has_resrc = True
                            break

                    if has_resrc or blueprint.reach_resrc_need(resource_need):
                        self.roleCtlr.new_work(btn.args["role"], WORK.BUILD, btn.args["id"])

                    self.right_buttons.clear()
                    self.right_selected = None

                elif btn.event == ASIGN_GO_STORAGE:
                    self.roleCtlr.new_work(btn.args["role"], WORK.OPEN_STORAGE, btn.args["id"])

                    self.right_buttons.clear()
                    self.right_selected = None
                return True
        return False

    def left_click(self, viewX, viewY):
        x, y = self.mouse_pos
        blk_sz = self.screen.block_size

        if self.full_ui:
            if x > 20 and x < 45:
                if y > 20 and y < 45:
                    self.full_ui = None

            button_press = self.detect_buttons(viewX, viewY)
            if button_press:
                return
            return

        if x < 100:
            if y > self.screen.height - 25:
                self.left_selected = (MENU_UI, )
                return

        if self.left_selected != None:
            if self.left_selected[0] == MENU_UI:
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
            elif self.left_selected[0] == NEW_BUILDING:
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

                self.buildCtlr.new_blueprint(
                    BluePrint(
                        self.left_selected[1].type,
                        (x, y),
                        rotate,
                        self.build_info
                        )
                    )

        # detect buttons
        button_press = self.detect_buttons(viewX, viewY)
        if button_press:
            return

        # detect role is clicked
        for role in self.roleCtlr.roles.values():
            if x < (role.x - viewX) * blk_sz:
                continue
            if x > (role.x - viewX) * blk_sz + blk_sz:
                continue

            if y < (role.y - viewY) * blk_sz:
                continue
            if y > (role.y - viewY) * blk_sz + blk_sz:
                continue
            
            self.left_selected = (ROLE, role.id)

            close_button = TextButton("X",
                self.font.f24,
                clr.red,
                CLOSE_ROLE_UI)
            close_button.set_pos((
                0,
                self.screen.height - INV_HEIGHT - 30,
                ))

            self.buttons.append(close_button)
            return

        self.buttons.clear()
        self.left_selected = None

    def right_click(self, viewX, viewY):
        x, y = self.mouse_pos
        col = y // self.screen.block_size + viewY

        blk_sz = self.screen.block_size

        # right click to chop tree
        if col in self.envCtlr.present_layer.draw_index:
            for row in self.envCtlr.present_layer.draw_index[col]:
                if x < (row - viewX) * blk_sz:
                    continue
                if x > (row - viewX) * blk_sz + blk_sz:
                    continue

                if y < (col - viewY) * blk_sz:
                    continue
                if y > (col - viewY) * blk_sz + blk_sz:
                    continue

                block = self.envCtlr.present_layer.map[col][row]
                if block == WOOD:
                    self.right_selected = (CHOP_TREE_UI, (row, col, ), )

                    self.right_buttons.clear()

                    y = col
                    for role in self.roleCtlr.roles:
                        self.right_buttons.append(Button(
                                (row, y),
                                (12, 2),
                                event=CHOP_TREE,
                                args={
                                    "role": role,
                                    "id":self.right_selected[1]},
                                floting=True,
                                text=self.font.get_16_text(
                                    f"Asign {role} to chop tree", clr.white)
                            ))
                        y += 2
                    return

        for blueprint in self.buildCtlr.blueprints.values():
            b_x = (blueprint.pos[0] - viewX) * blk_sz
            b_y = (blueprint.pos[1] - viewY) * blk_sz

            width = 0
            height = 0

            if blueprint.facing == F_RIGHT:
                if not (x > b_x and y > b_y):
                    continue
                width = blueprint.width * blk_sz
                height = blueprint.height * blk_sz
            elif blueprint.facing == F_LEFT:
                b_x += blk_sz
                b_y += blk_sz
                if not (x < b_x and y < b_y):
                    continue
                width = blueprint.width * blk_sz
                height = blueprint.height * blk_sz
            elif blueprint.facing == F_UP:
                b_y += blk_sz
                if not (x > b_x and y < b_y):
                    continue
                width = blueprint.height * blk_sz
                height = blueprint.width * blk_sz
            elif blueprint.facing == F_DOWN:
                b_x += blk_sz
                if not (x < b_x and y > b_y):
                    continue
                width = blueprint.height * blk_sz
                height = blueprint.width * blk_sz
            else:
                continue

            if math.fabs(x - b_x) > width:
                continue
            elif math.fabs(y - b_y) > height:
                continue

            self.right_selected = (NEW_BUILDING, blueprint.pos , )

            y = blueprint.pos[1]
            blueprint_type = self.build_info.buildings[blueprint.type]["name"]
            for role in self.roleCtlr.roles:
                self.right_buttons.append(
                    Button(
                        (blueprint.pos[0], y),
                        (13, 2),
                        event=ASIGN_BUILD,
                        args={
                            "role": role,
                            "id": id(blueprint)},
                        floting=True,
                        text=self.font.get_16_text(
                            f"Asign {role} to build {blueprint_type}",
                            clr.white)
                        )
                    )
                y += 2
            return

        for building in self.buildCtlr.buildings.values():
            if building.click(self.mouse_pos, viewX, viewY, blk_sz):
                if building.type == self.build_info.STORAGE:
                    self.right_selected = (REACT_STORAGE_UI, building.hitbox_lt , )

                    y = building.hitbox_rd[1] - 1
                    for role in self.roleCtlr.roles:
                        self.right_buttons.append(
                            Button(
                                (building.hitbox_lt[0], y),
                                (13, 2),
                                event=ASIGN_GO_STORAGE,
                                args={
                                    "role": role,
                                    "id": id(building)},
                                floting=True,
                                text=self.font.get_16_text(
                                    f"Asign {role} to go to This Storage",
                                    clr.white)
                                )
                            )
                        y += 2
                return

        self.right_buttons.clear()

        self.right_selected = None

    def draw_button(self, viewX, viewY):
        blk_sz = self.screen.block_size
        for btn in self.buttons:
            if isinstance(btn, TextButton):
                self.surface.blit(btn.surface, (btn.x, btn.y))
            elif isinstance(btn, Button):
                btn.render(self.surface, viewX, viewY, blk_sz)

        for btn in self.right_buttons:
            btn.render(self.surface, viewX, viewY, blk_sz)

    def display_role_UI(self, role):
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

    def open_building_ui(self, build_type, building_id, role_id):
        self.full_ui = ("Building", build_type, building_id, role_id)
        self.right_buttons.clear()

        x = 30
        y = 60

        role = self.roleCtlr.roles[role_id]
        for i, item in enumerate(role.inventory.slots):
            self.buttons.append(Button(
                pos=(x, y),
                size=(INV_ITEM_SIZE, INV_ITEM_SIZE),
                floting=False,
                bg_clr=None,
                event=ITEM_SELECT_UI,
                args={"item_index": i, "role":role.id}
                ))
            x += INV_ITEM_SIZE + 10

    def render(self, viewX, viewY):
        blk_sz = self.screen.block_size
        if self.full_ui:
            pygame.draw.rect(self.surface, clr.black_ui_bg,
                (20, 20, self.screen.width - 40, self.screen.height - 40))

            self.surface.blit(self.font.get_24_text("X", clr.red),
                (20, 20))

            if self.full_ui[0] == "Building":
                if self.full_ui[1] == self.build_info.STORAGE:
                    role = self.roleCtlr.roles[self.full_ui[3]]
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

                    self.display_role_UI(role)

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

            self.draw_button(viewX, viewY)
