from random import randint

class clr:
    white = (255, 255, 255)
    black = (0, 0, 0)
    red = (240, 20, 20)
    orange = (220, 150, 20)
    yellow = (220, 220, 20)
    green = (20, 240, 20)
    grass_green = (67, 160, 51)
    blue = (20, 180, 240)
    drak_blue = (20, 20, 240)
    purple = (220, 20, 220)
    gray = (125, 125, 125)

    @staticmethod
    def random(minc=0, maxc=255):
        return (randint(minc, maxc), randint(minc, maxc), randint(minc, maxc))