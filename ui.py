import pygame
import os
from color import clr

from pygame_extendtion import *
from role import WORK

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
CHOP_TREE = "chop_tree"

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

class Button:
    def __init__(self, pos, size, event=None, args=None):
        self.x, self.y = pos

        self.width, self.height = size
        self.event = event

        self.args = args

    def click(self, pos):
        x, y = pos
        if x > self.x and x < self.x + self.width:
            if y > self.y and y < self.y + self.height:
                return True
        return False

class TextButton:
    def __init__(self, text, font, color, event=None):
        self.surface = font.render(text, 1, color)

        self.width, self.height = font.size(text)
        self.x , self.y = 0, 0

        self.event = event

    def set_pos(self, pos):
        self.x, self.y = pos

    def click(self, pos):
        x, y = pos
        if x > self.x and x < self.x + self.width:
            if y > self.y and y < self.y + self.height:
                return True
        return False

class UIController:
    def __init__(self, screen_info):
        self.screen = screen_info
        self.surface = None
        self.roleCtlr = None
        self.envCtlr = None

        self.font = None
        self.close_icon = None

        self.left_selected = None
        self.right_selected = None
        self.buttons = []

        self.items_info = ItemInfo()

    def change_surface(self, surface):
        self.surface = surface

        self.font = Font()

    def setUpCtlr(self, envCtlr, roleCtlr):
        self.envCtlr = envCtlr
        self.roleCtlr = roleCtlr

        self.items_info.load("ItemInfo.json")

    def left_click(self, pos, viewX, viewY):
        x, y = pos

        if x < 100:
            if y > self.screen.height - 25:
                self.left_selected = (MENU_UI, )
                return

        # detect buttons
        for btn in self.buttons:
            if btn.click(pos):
                if btn.event == CLOSE_ROLE_UI:
                    self.buttons.remove(btn)
                    self.left_selected = None
                elif btn.event == CHOP_TREE:
                    self.roleCtlr.new_work(btn.args["role"], WORK.CHOP, btn.args["id"])

                    self.buttons.remove(btn)
                    self.right_selected = None
                return

        blk_sz = self.screen.block_size
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

        self.left_selected = None

    def right_click(self, pos, viewX, viewY):
        x, y = pos
        col = y // self.screen.block_size

        blk_sz = self.screen.block_size
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

                    for btn in self.buttons:
                        if btn.event == CHOP_TREE:
                            self.buttons.remove(btn)

                    for role in self.roleCtlr.roles:
                        self.buttons.append(
                            Button(
                                (x, y),
                                (150, 20),
                                CHOP_TREE,
                                {"role": role, "id":self.right_selected[1]})
                            )
                    return


        for btn in self.buttons:
            if btn.event == CHOP_TREE:
                self.buttons.remove(btn)
        self.right_selected = None

    def draw_button(self):
        for btn in self.buttons:
            if isinstance(btn, TextButton):
                self.surface.blit(btn.surface, (btn.x, btn.y))

    def display_role_UI(self, role):
        pygame.draw.rect(self.surface,
            clr.black_ui_bg,
            (0, self.screen.height - INV_HEIGHT - 30,
            INV_WIDTH, INV_HEIGHT),
            )

        self.draw_button()

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

    def render(self, viewX, viewY):
        pygame.draw.rect(self.surface, clr.black_ui_bg,
            (0, self.screen.height - 25, 100, 25))
        self.surface.blit(self.font.get_24_text("Menu", clr.white), (20, self.screen.height - 23))

        blk_sz = self.screen.block_size
        if self.left_selected != None:
            if self.left_selected[0] == ROLE:
                role = self.roleCtlr.roles[self.left_selected[1]]

                x = (role.x - viewX) * blk_sz
                y = (role.y - viewY) * blk_sz

                pygame.draw.rect(self.surface, clr.white,
                    (x, y, blk_sz, blk_sz), 2)

                self.display_role_UI(role)
            elif self.left_selected[0] == MENU_UI:
                pass

        if self.right_selected != None:
            if self.right_selected[0] == CHOP_TREE_UI:
                x = self.right_selected[1][0] * blk_sz
                y = self.right_selected[1][1] * blk_sz + blk_sz
                for role in self.roleCtlr.roles:
                    pygame.draw.rect(self.surface,
                        clr.black_ui_bg,
                        (x, y, 150, 20))

                    self.surface.blit(self.font.get_16_text(f"Asign {role} to chop tree", clr.white), (x + 20, y + 3))
                    y += 23
