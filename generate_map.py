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

	def gen_ground(self):
		hill = randint(1,3)
		self.extending = []

		for i in range(hill):
			cen_x = randint(0, self.width - 1)
			cen_y = randint(0, self.height - 1)

			self.map[cen_y][cen_x] = randint(20, 25)
			self.extending.append((cen_x, cen_y, ))

		self.gen_rock()

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

	def save(self, filepath):
		enviroment = f"{self.width}x{self.height}\n"
		for col in self.map:
			for cell in col:
				if cell == -1:
					enviroment += "0"
				else:
					enviroment += "1"
			enviroment += "\n"

		with open(filepath, "w") as file:
			file.write(enviroment)
	
	def print(self):
		# print("-" * self.width)
		for col in self.map:
			for cell in col:
				if cell == -1:
					cprint(" ", "green", "on_green", end="")
				else:
					cprint(" ", "grey", "on_grey", end="")
			print()

if __name__ == "__main__":
	app = App()
	app.gen_ground()
	app.print()
	save_or_not = input("Save? (y/n)")
	if save_or_not == "y":
		app.save("map/enviroment.txt")