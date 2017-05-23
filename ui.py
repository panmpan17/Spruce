import pygame
from color import clr

from pygame_extendtion import *

# object type
ROLE = "role"
INV_ITEM_SIZE = 35
INV_WIDTH = INV_ITEM_SIZE * 5 + 60
INV_HEIGHT = INV_ITEM_SIZE * 2 + 30

# button event
CLOSE_ROLE_UI = "cls_role_ui"

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

        self.font = None
        self.close_icon = None

        self.selected = None
        self.buttons = []

    def change_surface(self, surface):
        self.surface = surface

        self.font = pygame.font.Font(None, 24)

    def setUpCtlr(self, roleCtlr):
        self.roleCtlr = roleCtlr

    def click(self, pos, viewX, viewY):
        x, y = pos

        # detect buttons
        for btn in self.buttons:
            if btn.click(pos):
                if btn.event == CLOSE_ROLE_UI:
                    self.buttons.clear()
                    self.selected = None
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
            
            self.selected = (ROLE, role.id)

            close_button = TextButton("X",
                self.font,
                clr.red,
                CLOSE_ROLE_UI)
            close_button.set_pos((
                0,
                self.screen.height - INV_HEIGHT,
                ))

            self.buttons.append(close_button)
            break

    def draw_button(self):
        for btn in self.buttons:
            self.surface.blit(btn.surface,
                (btn.x, btn.y))

    def display_role_UI(self, role):
        pygame.draw.rect(self.surface,
            (46, 46, 48),
            (0, self.screen.height - INV_HEIGHT,
            INV_WIDTH, INV_HEIGHT),
            )

        self.draw_button()

        x = 10
        y = self.screen.height - INV_HEIGHT + 10
        for i in role.inventory.slots:
            pygame.draw.rect(self.surface,
                clr.white,
                (x, y, INV_ITEM_SIZE, INV_ITEM_SIZE),
                2)
            x += INV_ITEM_SIZE + 10
            if x >= INV_WIDTH:
                y += INV_ITEM_SIZE + 10
                x = 10

    def render(self, viewX, viewY):
        if self.selected != None:
            if self.selected[0] == ROLE:
                blk_sz = self.screen.block_size
                role = self.roleCtlr.roles[self.selected[1]]

                x = (role.x - viewX) * blk_sz
                y = (role.y - viewY) * blk_sz

                pygame.draw.rect(self.surface, clr.white,
                    (x, y, blk_sz, blk_sz), 2)

                self.display_role_UI(role)
