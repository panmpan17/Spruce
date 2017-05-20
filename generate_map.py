from pprint import pprint
from random import randint
from termcolor import cprint

RIGHT = (1, 0)
LEFT = (-1, 0)
UP = (0, 1)
DOWN = (0, -1)
ALL_DIRECTION = (RIGHT, LEFT, UP, DOWN)

class App:
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

if __name__ == "__main__":
    app = App()
    app.load("map/ground.txt")
    # app.gen_tree()
    app.save("map/ground.txt")