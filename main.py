import pygame
import animal
import building
import role
from color import clr

from platform import system as osSystem

from enviroment import EnviromentController, ScreenInfo

PLATFORM = osSystem()
WIDTH = 500
HEIGHT = 500
BLOCK_SIZE = 10

SCREEN = ScreenInfo(block_size=BLOCK_SIZE, width=WIDTH, height=HEIGHT)

BLK_SZ_LEVELS = (
    10,
    20,
    25
    )

WIDTH_BLOCKS = WIDTH / SCREEN.block_size
HEIGHT_BLOCKS = HEIGHT / SCREEN.block_size
QUIT = pygame.QUIT
MOUSEDOWN = pygame.MOUSEBUTTONDOWN
KEYDOWN = pygame.KEYDOWN

class App:
    def __init__(self):
        self.window = None
        self.envCtler = EnviromentController(SCREEN)
        self.block_size_level = BLK_SZ_LEVELS.index(BLOCK_SIZE)

    def load_map(self):
        self.envCtler.load("map/ground.txt")

    def zoom_in(self):
        if self.block_size_level < len(BLK_SZ_LEVELS) - 1:
            self.block_size_level += 1
            SCREEN.set_block_size(BLK_SZ_LEVELS[self.block_size_level])
            self.envCtler.change_screen_size()

    def zoom_out(self):
        if self.block_size_level >= 1:
            self.block_size_level -= 1
            SCREEN.set_block_size(BLK_SZ_LEVELS[self.block_size_level])
            self.envCtler.change_screen_size()

    def run(self):
        pygame.init()
        pygame.key.set_repeat(1, 20)

        self.window = pygame.display.set_mode((WIDTH, HEIGHT))
        self.envCtler.change_surface(self.window)
        clock = pygame.time.Clock()

        count = 0
        viewY = 0
        viewX = 0
        while True:
            self.envCtler.render(viewX, viewY)

            for event in pygame.event.get():
                if event.type == QUIT:
                    self.stop()
                if event.type == KEYDOWN:
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

            pygame.display.flip()
            clock.tick(30)

    def stop(self):
        self.envCtler.stop()
        pygame.quit()
        exit()

if __name__ == "__main__":
    app = App()
    app.load_map()
    app.run()