import pygame
import animal
import building
import role
from color import clr

from platform import system as osSystem

from pygame_extendtion import *
from enviroment import EnviromentController
from animal import AnimalController
from role import RoleController
from ui import UIController

from threading import Thread
from time import sleep

PLATFORM = osSystem()
WIDTH = 750
HEIGHT = 500
BLOCK_SIZE = 10

BLK_SZ_LEVELS = (
    10,
    20,
    25
    )

QUIT = pygame.QUIT
MOUSEDOWN = pygame.MOUSEBUTTONDOWN
KEYDOWN = pygame.KEYDOWN

class App:
    def __init__(self):
        self.window = None
        self.block_size_level = BLK_SZ_LEVELS.index(BLOCK_SIZE)
        self.screen = ScreenInfo(block_size=BLOCK_SIZE, width=WIDTH, height=HEIGHT)

        self.envCtlr = EnviromentController(self.screen)
        self.animalCtlr = AnimalController(self.screen)
        self.roleCtlr = RoleController(self.screen)

        self.UICtlr = UIController(self.screen)

        self.GameEngine = None
        self.STOP = False

    def load_map(self, mappath):
        self.envCtlr.load(mappath)
        self.animalCtlr.load(mappath)
        self.roleCtlr.load(mappath)

        self.animalCtlr.setUpCtlr(self.envCtlr, self.roleCtlr)

        self.UICtlr.setUpCtlr(self.roleCtlr)

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
        clock = pygame.time.Clock()
        while not self.STOP:
            self.animalCtlr.tick_load(1/tick)
            clock.tick(tick)

    def run(self):
        pygame.init()

        self.GameEngine = Thread(target=self.loadGameEngine)
        self.GameEngine.start()

        pygame.key.set_repeat(1, 20)

        self.window = pygame.display.set_mode((WIDTH, HEIGHT))
        self.envCtlr.change_surface(self.window)
        self.animalCtlr.change_surface(self.window)
        self.roleCtlr.change_surface(self.window)

        self.UICtlr.change_surface(self.window)

        pygame.display.set_caption("Spruce")


        clock = pygame.time.Clock()

        count = 0
        viewY = 0
        viewX = 0
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.stop()

                elif event.type == MOUSEDOWN:

                    self.UICtlr.click(event.pos, viewX, viewY)

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

                    # role movement
                    if keys[pygame.K_RIGHT]:
                        self.roleCtlr.roles[1].x += 1
                    elif keys[pygame.K_LEFT]:
                        self.roleCtlr.roles[1].x -= 1
                    if keys[pygame.K_UP]:
                        self.roleCtlr.roles[1].y -= 1
                    elif keys[pygame.K_DOWN]:
                        self.roleCtlr.roles[1].y += 1

                    # zoom
                    if keys[pygame.K_EQUALS]:
                        blz_size_level = self.block_size_level

                        if PLATFORM == "Darwin" and keys[pygame.K_LMETA]:
                            self.zoom_in()
                        elif keys[pygame.K_LMETA]:
                            self.zoom_in()
                    elif keys[pygame.K_MINUS]:
                        blz_size_level = self.block_size_level

                        if PLATFORM == "Darwin" and keys[pygame.K_LMETA]:
                            self.zoom_out()
                        elif keys[pygame.K_LMETA]:
                            self.zoom_out()

            self.envCtlr.render(viewX, viewY)
            self.animalCtlr.render(viewX, viewY)
            self.roleCtlr.render(viewX, viewY)

            self.UICtlr.render(viewX, viewY)
            pygame.display.flip()

            clock.tick(30)

    def stop(self):
        self.STOP = True
        pygame.quit()
        exit()

if __name__ == "__main__":
    app = App()
    app.load_map("map")
    app.run()