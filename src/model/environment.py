from math import cos, sin, radians
from PIL import ImageTk
from helpers.utils import norm, distance_between
from random import randint, random
import numpy as np

from model.agent import Agent
from model.behavior import DiffusiveBehavior, SocialBehavior


# Define a function for filling the rectangle with random colors
def rgb(r, g, b):
   return "#%s%s%s" % tuple([hex(c)[2:].rjust(2, "0")
      for c in (r, g, b)])


class Environment:

    def __init__(self, width=500, height=500,
                 nb_robots=30, robot_speed=3, robot_radius=5, communication_radius=25, draw_debug=True,
                 crw_factor=0.9, levy_factor=1.2,
                 bool_noise=1, noise_mu=0, noise_musd=1, noise_sd=0.1):
        self.population = list()
        self.width = width
        self.height = height
        self.nb_robots = nb_robots
        self.robot_speed = robot_speed
        self.robot_radius = robot_radius
        self.robot_communication_radius = communication_radius
        self.draw_debug = draw_debug
        self.crw_factor = crw_factor
        self.levy_factor = levy_factor
        self.bool_noise = bool_noise
        self.noise_mu = noise_mu
        self.noise_musd = noise_musd
        self.noise_sd = noise_sd
        self.create_robots()
        self.neighbors_table = [[] for i in range(len(self.population))]
        self.img = None

    def load_images(self):
        self.img = ImageTk.PhotoImage(file="../assets/field.png")


    def step(self):
        # compute neighbors
        pop_size = len(self.population)
        self.neighbors_table = [[] for i in range(pop_size)]
        for id1 in range(pop_size):
            for id2 in range(id1 + 1, pop_size):
                if distance_between(self.population[id1], self.population[id2]) < self.robot_communication_radius:
                    self.neighbors_table[id1].append(self.population[id2])
                    self.neighbors_table[id2].append(self.population[id1])

        # print(self.neighbors_table)
        # 2. Move
        for robot in self.population:
            robot.step()

    def create_robots(self):
        for robot_id in range(self.nb_robots):
            robot = Agent(robot_id=robot_id,
                          x=randint(self.robot_radius, self.width - 1 - self.robot_radius),
                          y=randint(self.robot_radius, self.height - 1 - self.robot_radius),
                          speed=self.robot_speed,
                          radius=self.robot_radius,
                          bool_noise=self.bool_noise,
                          noise_mu=self.noise_mu,
                          noise_musd=self.noise_musd,
                          noise_sd=self.noise_sd,
                          behavior=SocialBehavior(),
                          environment=self)
            self.population.append(robot)

    def get_sensors(self, robot):
        orientation = robot.orientation
        speed = robot.speed()
        sensors = {"GRADIENT": self.sense_gradient(robot),
                   "FRONT": any(self.check_border_collision(robot, robot.pos[0] + speed * cos(radians(orientation)),
                                                            robot.pos[1] + speed * sin(radians(orientation)))),
                   "RIGHT": any(
                       self.check_border_collision(robot, robot.pos[0] + speed * cos(radians((orientation - 90) % 360)),
                                                   robot.pos[1] + speed * sin(radians((orientation - 90) % 360)))),
                   "BACK": any(self.check_border_collision(robot, robot.pos[0] + speed * cos(
                       radians((orientation + 180) % 360)),
                                                           robot.pos[1] + speed * sin(
                                                               radians((orientation + 180) % 360)))),
                   "LEFT": any(
                       self.check_border_collision(robot, robot.pos[0] + speed * cos(radians((orientation + 90) % 360)),
                                                   robot.pos[1] + speed * sin(radians((orientation + 90) % 360)))),
                   "NEIGHBORS": self.sense_neighbors(robot),
                   }
        # print(sensors)
        return sensors

    def sense_gradient(self, robot):
        return 255 - (255 * robot.pos[0]) // self.width

    def check_border_collision(self, robot, new_x, new_y):
        collide_x = False
        collide_y = False
        if new_x + robot._radius >= self.width or new_x - robot._radius < 0:
            collide_x = True

        if new_y + robot._radius >= self.height or new_y - robot._radius < 0:
            collide_y = True

        return collide_x, collide_y

    def sense_neighbors(self, robot):
        return self.neighbors_table[robot.id]

    def draw(self, canvas):
        # self.draw_gradient_background(canvas)
        # self.draw_background(canvas)
        for robot in self.population:
            robot.draw(canvas, self.draw_debug)

    def get_robot_at(self, x, y):
        selected = None
        for bot in self.population:
            if norm(bot.pos - np.array([x, y]).astype('float64')) < self.robot_radius:
                selected = bot
                break
        return selected

    def switch_draw_trace(self):
        self.draw_debug = not self.draw_debug

    def draw_gradient_background(self, canvas):
        # Iterate through the color and fill the rectangle with colors(r,g,0)
        # for x in range(0, 256):
        #     r = (255 - x)
        #     g = (255 - x)
        #     # g = 255 if x < 128 else 255 - (x - 128) * 2
        #     b = (255 - x)
        #     print(x, g)
        #     canvas.create_rectangle(x * 2, 0, self.width, self.height, fill=rgb(r, g, b), outline=rgb(r, g, b))
        #     # canvas.create_rectangle(x * 2, 0, self.width, self.height, fill=rgb(0, g, 0), outline=rgb(0, g, 0))
        for x in range(0, self.width+1):
            r = 255 - (x * 255) // self.width
            g = 255 - (x * 255) // self.width
            # g = 255 if x < 128 else 255 - (x - 128) * 2
            b = 255 - (x * 255) // self.width
            # print(x, g)
            # canvas.create_rectangle(x, 0, self.width, self.height, fill=rgb(0, g, 0), outline=rgb(0, g, 0))
            canvas.create_rectangle(x, 0, self.width, self.height, fill=rgb(r, g, b), outline=rgb(r, g, b))

    def draw_background(self, canvas):
        canvas.create_image(0, 0, image=self.img, anchor='nw')
