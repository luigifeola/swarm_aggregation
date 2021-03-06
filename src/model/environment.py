from math import cos, sin, radians
from PIL import ImageTk, Image
from helpers.utils import norm, distance_between, matrix_index_distances, rgb, get_pixel_col
from random import randint, random
import numpy as np
import igraph as ig

from model.agent import Agent
from model.behavior import DiffusiveBehavior, SocialBehavior
from helpers import random_walk

START_CRW_FACTOR = 0.9
START_LEVY_FACTOR = 1.2
START_MAX_STRAIGHT_STEP = 1000


class Environment:

    def __init__(self, width=500, height=500,
                 nb_robots=30, robot_speed=3, robot_radius=5, communication_radius=25, quantization_bits=3,
                 draw_trace_debug=True, draw_communication_range_debug=True,
                 bool_noise=1, noise_mu=0, noise_musd=1, noise_sd=0.1, robot_behavior=1):
        self.population = list()
        self.width = width
        self.height = height
        self.nb_robots = nb_robots
        self.robot_speed = robot_speed
        self.robot_radius = robot_radius
        self.robot_communication_radius = communication_radius
        self.quantization_bits = quantization_bits
        self.perceptible_gradient = None
        self.draw_trace_debug = draw_trace_debug
        self.draw_communication_range_debug = draw_communication_range_debug
        self.bool_noise = bool_noise
        self.noise_mu = noise_mu
        self.noise_musd = noise_musd
        self.noise_sd = noise_sd
        self.robot_behavior = robot_behavior
        self.create_robots()
        self.neighbors_table = [[] for i in range(len(self.population))]
        self.img = None
        self.background = self.create_environment()
        self.init_robot_parameters()
        self.sensed_gradient = 0
        self.metrics = ["cluster_number,cluster_metric"]

    def load_images(self):
        self.img = ImageTk.PhotoImage(file="../assets/field.png")


    def step(self):
        #1. Compute neighbors
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

        #3. Compute metrics
        total_distance = 0
        for robot1 in self.population:
            for robot2 in self.population:
                if robot1 != robot2:
                    total_distance += distance_between(robot1, robot2)
        total_distance = -total_distance
        # print("Total distance = %s" % total_distance)

        clusters = self.get_neighbors_graph().clusters()
        # print("Number of clusters = %d" % len(clusters))
        max = 0
        cluster_count = len(clusters)
        for cluster in clusters:
            if(len(cluster) > max):
                max = len(cluster)
            # if(len(cluster)==1):
            #     cluster_count -= 1

        # print("Largest cluster size = %d" % max)
        cluster_metric = max/pop_size
        # print("Cluster metric = %f" % cluster_metric)

        self.metrics.append(str(cluster_count) + "," + str(cluster_metric))


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
                          behavior=DiffusiveBehavior() if self.robot_behavior == 1 else SocialBehavior(),
                          environment=self)
            self.population.append(robot)

    def create_environment(self):
        background = Image.new('L', (self.width, self.height))
        outerColor = 255
        innerColor = 0
        center_gradient = np.array([randint(0, self.width), randint(0, self.height)])
        # Make it on a scale from 0 to 1
        max_gradient_width = max(self.width - center_gradient[0], center_gradient[0])
        max_gradient_height = max(self.height - center_gradient[1], center_gradient[1])
        max_distance = max(max_gradient_width, max_gradient_height)
        distances = matrix_index_distances(np.zeros((self.width, self.height)), index=center_gradient)
        distances = distances / max_distance
        for y in range(0, self.height, 2):
            for x in range(0, self.width, 2):
                # Find the distance to the center
                distanceToCenter = distances[x, y]
                gray = int(outerColor * distanceToCenter + innerColor * (1 - distanceToCenter))
                background.putpixel((x, y), gray)
                background.putpixel((x + 1, y), gray)
                background.putpixel((x, y + 1), gray)
                background.putpixel((x + 1, y + 1), gray)

        return background

    def init_robot_parameters(self):
        random_walk.set_parameters(START_CRW_FACTOR, START_LEVY_FACTOR, START_MAX_STRAIGHT_STEP)
        random_walk.init_values(self.quantization_bits)
        self.perceptible_gradient = np.linspace(0.2, 1.0, num=self.quantization_bits)
        # print('perceptible_gradient ', self.perceptible_gradient)

    def get_sensors(self, robot):
        orientation = robot.orientation
        speed = robot.speed()
        sensors = {"GRADIENT": self.sense_gradient(robot),
                   "FRONT": any(
                       self.check_border_collision(robot,
                                                   robot.pos[0] + speed * cos(radians(orientation)),
                                                   robot.pos[1] + speed * sin(radians(orientation)))),
                   "RIGHT": any(
                       self.check_border_collision(robot,
                                                   robot.pos[0] + speed * cos(radians((orientation - 90) % 360)),
                                                   robot.pos[1] + speed * sin(radians((orientation - 90) % 360)))),
                   "BACK": any(
                       self.check_border_collision(robot,
                                                   robot.pos[0] + speed * cos(radians((orientation + 180) % 360)),
                                                   robot.pos[1] + speed * sin(radians((orientation + 180) % 360)))),
                   "LEFT": any(
                       self.check_border_collision(robot,
                                                   robot.pos[0] + speed * cos(radians((orientation + 90) % 360)),
                                                   robot.pos[1] + speed * sin(radians((orientation + 90) % 360)))),
                   "NEIGHBORS": self.sense_neighbors(robot),
                   }
        # print(sensors)
        return sensors

    def sense_gradient(self, robot):
        # return 255 - (255 * robot.pos[0]) // self.width
        gradient_t = get_pixel_col(self.background, robot.pos)
        self.sensed_gradient += gradient_t
        return gradient_t

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

    def get_neighbors_graph(self):
        edges = []
        for i in range(len(self.neighbors_table)):
            for j in range(len(self.neighbors_table[i])):
                edges.append((i,int(self.neighbors_table[i][j].id)))

        graph = ig.Graph(edges= edges)
        return graph

    def draw(self, canvas):
        # self.draw_gradient_background(canvas)
        self.draw_background(canvas)
        for robot in self.population:
            robot.draw(canvas, self.draw_trace_debug, self.draw_communication_range_debug)

    def get_robot_at(self, x, y):
        selected = None
        for bot in self.population:
            if norm(bot.pos - np.array([x, y]).astype('float64')) < self.robot_radius:
                selected = bot
                break
        return selected

    def get_perceptible_gradient(self):
        return self.perceptible_gradient

    def switch_draw_trace(self):
        self.draw_trace_debug = not self.draw_trace_debug

    def switch_draw_communication_range(self):
        self.draw_communication_range_debug = not self.draw_communication_range_debug

    def draw_gradient_background(self, canvas):
        # Iterate through the color and fill the rectangle with colors(r,g,0)
        for x in range(0, self.width + 1):
            r = 255 - (x * 255) // self.width
            g = 255 - (x * 255) // self.width
            # g = 255 if x < 128 else 255 - (x - 128) * 2
            b = 255 - (x * 255) // self.width
            # print(x, g)
            # canvas.create_rectangle(x, 0, self.width, self.height, fill=rgb(0, g, 0), outline=rgb(0, g, 0))
            canvas.create_rectangle(x, 0, self.width, self.height, fill=rgb(r, g, b), outline=rgb(r, g, b))

    def draw_background(self, canvas):
        self.img = ImageTk.PhotoImage(self.background)
        canvas.create_image(0, 0, image=self.img, anchor='nw')
