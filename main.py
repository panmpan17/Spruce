import pygame
import animal
import building
import role
from color import clr

from platform import system as osSystem

from pygame_extendtion import *
from enviroment import EnviromentController
from animal import AnimalController, AnimalInfo
from role import RoleController
from ui import UIController, ItemInfo
from building import BuildingController, BuildingInfo

from threading import Thread
from time import sleep

PLATFORM = osSystem()
WIDTH = 760
HEIGHT = 500
BLOCK_SIZE = 20

BLK_SZ_LEVELS = (
    10,
    20,
    25,
    50
    )

QUIT = pygame.QUIT
MOUSEDOWN = pygame.MOUSEBUTTONDOWN
KEYDOWN = pygame.KEYDOWN

class App:
    def __init__(self):
        self.window = None
        self.block_size_level = BLK_SZ_LEVELS.index(BLOCK_SIZE)

        self.screen = ScreenInfo(block_size=BLOCK_SIZE, width=WIDTH, height=HEIGHT)
        self.images = ImageLoader()
        self.images.load_directory("texture")

        self.build_info = BuildingInfo()
        self.build_info.load("info/BuildingInfo.json", self.images)

        self.items_info = ItemInfo()
        self.items_info.load("info/ItemInfo.json", self.images)

        self.animals_info = AnimalInfo()
        self.animals_info.load("info/Animal.json", self.images)

        self.envCtlr = EnviromentController(
            self.screen,
            self.images)
        self.animalCtlr = AnimalController(
            self.screen,
            self.animals_info,
            self.images)
        self.roleCtlr = RoleController(
            self.screen,
            self.images,
            self.build_info)
        self.buildCtlr = BuildingController(
            self.screen,
            self.images,
            self.build_info,
            self.items_info,
            self.animals_info)
        self.UICtlr = UIController(
            self.screen,
            self.build_info,
            self.items_info)

        self.GameEngine = None
        self.STOP = False

    def load_map(self, mappath):
        self.envCtlr.load(mappath)
        self.animalCtlr.load(mappath)
        self.roleCtlr.load(mappath)
        self.buildCtlr.load(mappath)

        self.animalCtlr.setUpCtlr(
            self.envCtlr,
            self.roleCtlr)

        self.roleCtlr.setUpCtlr(
            self.envCtlr,
            self.animalCtlr,
            self.buildCtlr,
            self.UICtlr
            )

        self.buildCtlr.setUpCtlr(
            self.envCtlr,
            )

        self.UICtlr.setUpCtlr(
            self.envCtlr,
            self.roleCtlr,
            self.buildCtlr,
            self.animalCtlr,
            )

    def zoom_in(self):
        if self.block_size_level < len(BLK_SZ_LEVELS) - 1:
            self.block_size_level += 1
            self.screen.set_block_size(BLK_SZ_LEVELS[self.block_size_level])
            self.envCtlr.change_screen_size()

    def zoom_out(self):
        if self.block_size_level >= 1:
            self.block_size_level -= 1
            self.screen.set_block_size(BLK_SZ_LEVELS[self.block_size_level])
            self.envCtlr.change_screen_size()

    def loadGameEngine(self):
        tick = 30
        tick_interval = 1 / tick
        clock = pygame.time.Clock()
        while not self.STOP:
            self.animalCtlr.tick_load(tick_interval)
            self.roleCtlr.tick_load(tick_interval)
            self.buildCtlr.tick_load(tick_interval)
            clock.tick(tick)

    def set_up(self):
        pygame.init()

        self.GameEngine = Thread(target=self.loadGameEngine)

        self.window = pygame.display.set_mode((WIDTH, HEIGHT))
        self.envCtlr.change_surface(self.window)
        self.animalCtlr.change_surface(self.window)
        self.roleCtlr.change_surface(self.window)
        self.buildCtlr.change_surface(self.window)

        self.UICtlr.change_surface(self.window)

        pygame.key.set_repeat(1, 20)
        pygame.display.set_caption("Spruce")

    def run(self):
        self.set_up()

        self.GameEngine.start()
        clock = pygame.time.Clock()

        count = 0
        viewY = 0
        viewX = 0
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.stop()
                elif event.type == MOUSEDOWN:
                    if event.button == 1:
                        self.UICtlr.left_click(viewX, viewY)
                    elif event.button == 3:
                        self.UICtlr.right_click(viewX, viewY)

                elif event.type == KEYDOWN:
                    keys = pygame.key.get_pressed()

                    camera_moved = False
                    # move camera
                    if keys[pygame.K_w]:
                        if viewY >= 0:
                            viewY -= 1
                            camera_moved = True
                    elif keys[pygame.K_s]:
                        if self.envCtlr.in_y_view(viewY):
                            viewY += 1
                            camera_moved = True

                    if keys[pygame.K_a]:
                        if viewX >= 0:
                            viewX -= 1
                            camera_moved = True
                    elif keys[pygame.K_d]:
                        if self.envCtlr.in_x_view(viewX):
                            viewX += 1
                            camera_moved = True
                    if camera_moved:
                        continue

                    # building rotate
                    if keys[pygame.K_q]:
                        self.UICtlr.press(pygame.K_q)
                    elif keys[pygame.K_e]:
                        self.UICtlr.press(pygame.K_e)

                    # change envirment
                    if keys[pygame.K_UP]:
                        viewX, viewY = self.envCtlr.change_depth(1, viewX, viewY)
                        self.UICtlr.clear_buttons()
                    elif keys[pygame.K_DOWN]:
                        viewX, viewY = self.envCtlr.change_depth(-1, viewX, viewY)
                        self.UICtlr.clear_buttons()

                    # zoom
                    if keys[pygame.K_EQUALS]:
                        blz_size_level = self.block_size_level

                        if PLATFORM == "Darwin" and (keys[pygame.K_LMETA] or keys[pygame.K_RMETA]):
                            self.zoom_in()
                        elif keys[pygame.K_LMETA] or keys[pygame.K_RMETA]:
                            self.zoom_in()
                    elif keys[pygame.K_MINUS]:
                        blz_size_level = self.block_size_level

                        if PLATFORM == "Darwin" and (keys[pygame.K_LMETA] or keys[pygame.K_RMETA]):
                            self.zoom_out()
                        elif keys[pygame.K_LMETA] or keys[pygame.K_RMETA]:
                            self.zoom_out()
                elif event.type == pygame.MOUSEMOTION:
                    self.UICtlr.mouse_motion(event.pos)

            self.envCtlr.render(viewX, viewY)
            self.buildCtlr.render(viewX, viewY)
            self.animalCtlr.render(viewX, viewY)
            self.roleCtlr.render(viewX, viewY)

            self.UICtlr.render(viewX, viewY)
            pygame.display.flip()

            clock.tick(30)

    def stop(self):
        self.STOP = True
        self.envCtlr.stop()
        pygame.quit()
        exit()

if __name__ == "__main__":
    app = App()
    app.load_map("map")
    app.run()