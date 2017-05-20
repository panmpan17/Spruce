import pygame
import animal
import building
import role
from color import clr

from platform import system as osSystem

from enviroment import EnviromentController
from animal import AnimalController
from pygame_extendtion import *

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

        self.envCtler = EnviromentController(self.screen)
        self.animalCtler = AnimalController(self.screen)

        self.GameEngine = None
        self.STOP = False

    def load_map(self, mappath):
        self.envCtler.load(mappath)
        self.animalCtler.load(mappath)

        self.animalCtler.setUpCtlr(self.envCtler)

    def zoom_in(self):
        if self.block_size_level < len(BLK_SZ_LEVELS) - 1:
            self.block_size_level += 1
            self.screen.set_block_size(BLK_SZ_LEVELS[self.block_size_level])
            self.envCtler.change_screen_size()
            pygame.event.post(MyPygameEvent.VBUPDATE)

    def zoom_out(self):
        if self.block_size_level >= 1:
            self.block_size_level -= 1
            self.screen.set_block_size(BLK_SZ_LEVELS[self.block_size_level])
            self.envCtler.change_screen_size()
            pygame.event.post(MyPygameEvent.VBUPDATE)

    def loadGameEngine(self):
        tick = 10
        clock = pygame.time.Clock()
        while not self.STOP:
            self.animalCtler.tick_load(1/tick)
            clock.tick(tick)

    def run(self):
        pygame.init()

        self.GameEngine = Thread(target=self.loadGameEngine)
        self.GameEngine.start()

        pygame.key.set_repeat(1, 20)

        self.window = pygame.display.set_mode((WIDTH, HEIGHT))
        self.envCtler.change_surface(self.window)
        self.animalCtler.change_surface(self.window)

        pygame.display.set_caption("Spruce")


        clock = pygame.time.Clock()

        pygame.event.post(MyPygameEvent.VBUPDATE)
        count = 0
        viewY = 0
        viewX = 0
        while True:
            for event in pygame.event.get():
                # print(event.type)
                if event.type == QUIT:
                    self.stop()
                elif event.type == KEYDOWN:
                    keys = pygame.key.get_pressed()

                    camera_moved = False
                    # move camera
                    if keys[pygame.K_w]:
                        if viewY >= 0:
                            viewY -= 1
                            camera_moved = True
                    elif keys[pygame.K_s]:
                        if self.envCtler.in_y_view(viewY):
                            viewY += 1
                            camera_moved = True

                    if keys[pygame.K_a]:
                        if viewX >= 0:
                            viewX -= 1
                            camera_moved = True
                    elif keys[pygame.K_d]:
                        if self.envCtler.in_x_view(viewX):
                            viewX += 1
                            camera_moved = True
                    if camera_moved:
                        pygame.event.post(MyPygameEvent.VBUPDATE)
                        continue

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

                elif event.type == MyPygameEvent.VBUPDATE.type:
                    self.envCtler.render(viewX, viewY)
                    self.animalCtler.render(viewX, viewY)
                    pygame.display.flip()

            clock.tick(30)

    def stop(self):
        self.STOP = True
        # self.GameEngine.terminate()
        pygame.quit()
        exit()

if __name__ == "__main__":
    app = App()
    app.load_map("map")
    app.run()