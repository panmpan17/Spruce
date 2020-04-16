from pprint import pprint
from random import randint
from termcolor import cprint

RIGHT = (1, 0)
LEFT = (-1, 0)
UP = (0, 1)
DOWN = (0, -1)
ALL_DIRECTION = (RIGHT, LEFT, UP, DOWN)

class GroundMap:
    def __init__(self, width=100, height=100):
        self.width = width
        self.height = height
        self.map = []
        self.extending = None

        for i in range(height):
            self.map.append([-1] * width)

    def load(self, filepath):
        with open(filepath) as file:
            read = file.read()
        info = read.split("\n")
        width, height = info[0].split("x")
        width, height = int(width), int(height)

        map_ = []
        for i in range(1, len(info)):
            col = []
            for count, e in enumerate(info[i]):
                col.append(e)
            map_.append(col)
        self.map = map_
        self.width = width
        self.height = height

    def gen_ground(self):
        hill = randint(1,3)
        self.extending = []

        for i in range(hill):
            cen_x = randint(0, self.width - 1)
            cen_y = randint(0, self.height - 1)

            self.map[cen_y][cen_x] = randint(20, 25)
            self.extending.append((cen_x, cen_y, ))

        self.gen_rock()
        self.turn_rock()

    def gen_rock(self):
        if len(self.extending) == 0:
            return None
        else:
            new_extending = []
            for extend in self.extending:
                x, y = extend
                radius = self.map[y][x]
                self.map[y][x] = 0

                for direction in ALL_DIRECTION:
                    x_now, y_now = x, y

                    radius_now = randint(0, radius - 1)

                    xvector, yvector = direction
                    while radius_now > 0:
                        try:
                            if self.map[y_now + yvector][x_now + xvector] == -1:
                                x_now += xvector
                                y_now += yvector
                                self.map[y_now][x_now] = radius_now
                                new_extending.append((x_now, y_now))
                            radius_now -= 1
                        except:
                            radius_now -= 1

            self.extending = new_extending
            self.gen_rock()

    def turn_rock(self):
        for col in self.map:
            for cell in col:

                if cell == -1:
                    col[col.index(cell)] = "0"
                else:
                    col[col.index(cell)] = "1"

    def gen_tree(self):
        gen_num = randint(15, 20)
        count = 0

        while True:
            if count > gen_num:
                break
            x, y = randint(0, self.width - 1), randint(0, self.height - 1)
            if self.map[y][x] == "0":
                self.map[y][x] = "2"
            count += 1

    def save(self, filepath):
        enviroment = f"{self.width}x{self.height}\n"
        for col in self.map:
            for cell in col:
                enviroment += str(cell)
            enviroment += "\n"

        with open(filepath, "w") as file:
            file.write(enviroment)

    def print(self):
        # print("-" * self.width)
        for col in self.map:
            for cell in col:
                if cell == "0":
                    cprint(" ", "green", "on_green", end="")
                elif cell == "1":
                    cprint(" ", "grey", "on_grey", end="")
                elif cell == "2":
                    cprint(" ", "red", "on_red", end="")
            print()

STONE = "1"
COAL = "3"
COPPER = "4"
IRON = "5"
GOLD = "6"
ore_prop = {
    "1": 75, # stone
    "3": 10, # coal
    "4": 8,  # copper
    "5": 5,  # iron
    "6": 2,  # gold
    }
class UnderGroundMap:

    def __init__(self, width=200, height=200):
        self.width = width
        self.height = height
        self.map = []
        self.extending = None

        one_percent = (width * height) // 100
        self.coal = ore_prop[COAL] * one_percent
        self.copper = ore_prop[COPPER] * one_percent
        self.iron = ore_prop[IRON] * one_percent
        self.gold = ore_prop[GOLD] * one_percent

        for i in range(height):
            self.map.append([STONE] * width)

    def find_around(self, x, y):
        blocks = []
        if self.map[y][x] == STONE:
            blocks.append((x, y))
        else:
            return blocks

        for vx, vy in ALL_DIRECTION:
            try:
                if self.map[y + vy][x + vx] == STONE:
                    blocks.append((x + vx, y + vy))
            except:
                pass
        return blocks

    def gen_ore(self):
        while self.coal > 0:
            x = randint(0, self.width - 1)
            y = randint(0, self.height - 1)
            blocks = self.find_around(x, y)

            for block in blocks:
                self.coal -= 1
                self.map[block[1]][block[0]] = COAL

                if self.coal == 0:
                    break

        while self.copper > 0:
            x = randint(0, self.width - 1)
            y = randint(0, self.height - 1)
            blocks = self.find_around(x, y)

            for block in blocks:
                self.copper -= 1
                self.map[block[1]][block[0]] = COPPER

                if self.copper == 0:
                    break


        while self.iron > 0:
            x = randint(0, self.width - 1)
            y = randint(0, self.height - 1)
            blocks = self.find_around(x, y)

            for block in blocks:
                self.iron -= 1
                self.map[block[1]][block[0]] = IRON

                if self.iron == 0:
                    break


        while self.gold > 0:
            x = randint(0, self.width - 1)
            y = randint(0, self.height - 1)
            blocks = self.find_around(x, y)

            for block in blocks:
                self.gold -= 1
                self.map[block[1]][block[0]] = GOLD

                if self.gold == 0:
                    break


    def print(self):
        # print("-" * self.width)
        for col in self.map:
            for cell in col:
                if cell == "1":
                    cprint(" ", "white", "on_white", end="")
                elif cell == "3":
                    cprint(" ", "grey", "on_grey", end="")
                elif cell == "4":
                    cprint(" ", "magenta", "on_magenta", end="")
                elif cell == "5":
                    cprint(" ", "red", "on_red", end="")
                elif cell == "6":
                    cprint(" ", "yellow", "on_yellow", end="")
            print()

    def save(self, filepath):
        enviroment = f"{self.width}x{self.height}\n"
        for col in self.map:
            for cell in col:
                enviroment += str(cell)
            enviroment += "\n"

        with open(filepath, "w") as file:
            file.write(enviroment)


if __name__ == "__main__":
    ground = GroundMap()
    ground.gen_ground()
    # ground.gen_rock()
    ground.gen_tree()
    ground.save("map/ground.txt")
    under_ground = UnderGroundMap()
    under_ground.gen_ore()
    under_ground.save("map/underground.txt")
