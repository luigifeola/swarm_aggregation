import os
from math import cos, sin, radians
from helpers.utils import norm, distance_between, matrix_index_distances, get_pixel_col
import random
import numpy as np
import igraph as ig


from model.agent import Agent
from model.behavior import DiffusiveBehavior, SocialBehavior
from helpers import random_walk
from bisect import bisect


class Environment:

    def __init__(self,
                 crw_params, levy_params, std_motion_steps, quantization_bits=3, reset_jump=1,
                 width=500, height=500,
                 center_gradient=[500//2, 500//2], diffusion_type='linear', fixed_extension=1, fixed_position=1,
                 quantize_background=0,
                 nb_robots=30, robot_speed=3, robot_radius=5, communication_radius=25,
                 draw_trace_debug=False, draw_communication_range_debug=False,
                 bool_noise=1, noise_mu=0, noise_musd=1, noise_sd=0.1):
        self.population = list()
        self.width = width
        self.height = height
        self.center_gradient = center_gradient
        self.diffusion_type = diffusion_type
        self.fixed_extension = fixed_extension
        self.fixed_position = fixed_position
        self.quantize_background = quantize_background
        self.nb_robots = nb_robots
        self.robot_speed = robot_speed
        self.robot_radius = robot_radius
        self.robot_communication_radius = communication_radius
        self.quantization_bits = quantization_bits
        self.crw_params = crw_params
        self.levy_params = levy_params
        self.std_motion_steps = std_motion_steps
        self.reset_jump = bool(reset_jump)
        self.perceptible_gradient = None
        self.perceptible_thresholds = None
        self.draw_trace_debug = draw_trace_debug
        self.draw_communication_range_debug = draw_communication_range_debug
        self.bool_noise = bool_noise
        self.noise_mu = noise_mu
        self.noise_musd = noise_musd
        self.noise_sd = noise_sd
        self.create_robots()
        self.neighbors_table = [[] for i in range(len(self.population))]
        self.img = None
        self.init_robot_parameters()
        if quantize_background:
            self.quantized_background = np.ones([self.width, self.height])
        else:
            self.quantized_background = None
        self.background = self.create_environment(self.quantize_background)
        self.sensed_gradient = 0
        self.metrics = ["cluster_number,cluster_metric"]
        self.filepath = f"../data"
        self.robotPosFile = f"%5d_robotPos.txt" % (random.randint(0, 9999))
        self.make_logFiles()
        self.tick = 0



    def step(self):
        # 1. Compute neighbors
        pop_size = len(self.population)
        self.neighbors_table = [[] for i in range(pop_size)]
        for id1 in range(pop_size):
            for id2 in range(id1 + 1, pop_size):
                if distance_between(self.population[id1], self.population[id2]) < self.robot_communication_radius:
                    self.neighbors_table[id1].append(self.population[id2])
                    self.neighbors_table[id2].append(self.population[id1])

        # you should get the timestep from the main controller
        # with open(f"{self.filepath}/{self.robotPosFile}", "a") as file:
        #     file.write(f"{}\t")
        with open(f"{self.filepath}/robot_positions/{self.robotPosFile}", "a") as file:
            file.write(f"{self.tick}\t")
        for robot in self.population:
            r_pos = np.around(robot.pos, decimals=3)
            with open(f"{self.filepath}/robot_positions/{self.robotPosFile}", "a") as file:
                file.write(f"{r_pos[0]}\t"
                           f"{r_pos[1]}\t")

            robot.step()

        with open(f"{self.filepath}/robot_positions/{self.robotPosFile}", "a") as file:
            file.write(f"\n")

        self.tick += 1
        # # 3. Compute metrics
        # total_distance = 0
        # for robot1 in self.population:
        #     for robot2 in self.population:
        #         if robot1 != robot2:
        #             total_distance += distance_between(robot1, robot2)
        # total_distance = -total_distance
        # # print("Total distance = %s" % total_distance)
        #
        # clusters = self.get_neighbors_graph().clusters()
        # # print("Number of clusters = %d" % len(clusters))
        # max_val = 0
        # cluster_count = len(clusters)
        # for cluster in clusters:
        #     if len(cluster) > max:
        #         max = len(cluster)
        #     # if(len(cluster)==1):
        #     #     cluster_count -= 1
        #
        # # print("Largest cluster size = %d" % max)
        # cluster_metric = max_val / pop_size
        # # print("Cluster metric = %f" % cluster_metric)
        #
        # self.metrics.append(str(cluster_count) + "," + str(cluster_metric))


    def create_robots(self):
        for robot_id in range(self.nb_robots):
            robot = Agent(robot_id=robot_id,
                          x=random.randint(self.robot_radius, self.width - 1 - self.robot_radius),
                          y=random.randint(self.robot_radius, self.height - 1 - self.robot_radius),
                          speed=self.robot_speed,
                          radius=self.robot_radius,
                          bool_noise=self.bool_noise,
                          noise_mu=self.noise_mu,
                          noise_musd=self.noise_musd,
                          noise_sd=self.noise_sd,
                          behavior=DiffusiveBehavior(self.reset_jump),
                          # TODO: find a better way to switch among behaviours
                          # behavior=SocialBehavior(),
                          environment=self)
            self.population.append(robot)


    def make_logFiles(self):
        os.makedirs(self.filepath, exist_ok=True)


    @staticmethod
    def pixel_filter(val):
        if val < 0:
            val = 0
        if val > 255:
            val = 255
        return val

    def quantize_pixel(self, val):
        index = bisect(self.perceptible_thresholds[:-1], val / 255)
        quantized_val = 255 * self.perceptible_gradient[index - 1]
        return quantized_val

    @staticmethod
    def quadratic_diffusion(k_val, distance):
        distance = distance + 0.8 / k_val
        return 255 - int(255 / (distance * k_val) ** 2)


    @staticmethod
    def linear_diffusion(max_distance, distance):
        distance = distance / max_distance
        return int(255 * distance + 0 * (1 - distance / max_distance))


    def create_environment(self, q_background):
        # Random center position
        if not self.fixed_position:
            rand_x = random.randint(0, self.width)
            rand_y = random.randint(0, self.height)
            self.center_gradient = np.array([rand_x, rand_y])
        else:
            self.center_gradient = np.array([self.width // 2, self.width // 2])


        background = 255 * np.ones([self.width, self.height])

        if self.fixed_extension:
            max_distance = self.width // 2
            k_val = np.round(1 / (self.width // 4), 6)
        else:
            max_distance = random.randint(self.width // 3, self.width)
            k_val = np.round(np.random.uniform(1 / (self.width/4), 1 / (self.width/2)), 6)


        distances_from_center = matrix_index_distances(np.zeros((self.width, self.height)), index=self.center_gradient)

        for y in range(0, self.height, 2):
            for x in range(0, self.width, 2):

                if self.diffusion_type == 'linear':
                    gray = self.linear_diffusion(max_distance, distances_from_center[x, y])

                elif self.diffusion_type == 'quadratic':
                    gray = self.quadratic_diffusion(k_val, distances_from_center[x, y])

                else:
                    print('Wrong diffusion type!!!')
                    exit(-1)

                gray = self.pixel_filter(gray)
                if self.quantize_background:
                    quantized_gray = self.quantize_pixel(gray)
                    self.quantized_background[x, y] = quantized_gray
                    self.quantized_background[x + 1, y] = quantized_gray
                    self.quantized_background[x, y + 1] = quantized_gray
                    self.quantized_background[x + 1, y + 1] = quantized_gray

                background[x, y] = gray
                background[x+1, y] = gray
                background[x, y+1] = gray
                background[x+1, y+1] = gray

        # print('background.shape: ', background.shape)
        # print('background.shape: ', background.size)
        # print('pixels val sum / num of pixels / 255: ', np.sum(background)/background.size/255)
        # linear ---> .7366902396514161
        # quadratic 3 ---> .7684166448801742


        return background

    def init_robot_parameters(self):

        random_walk.init_values(self.crw_params, self.levy_params, self.std_motion_steps)
        self.perceptible_gradient = np.round(np.linspace(0.0, 1.0, num=self.quantization_bits), 2)
        self.perceptible_thresholds = np.round(np.linspace(0.0, 1.0, num=self.quantization_bits+1), 2)

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
        gradient_t = get_pixel_col(self.background, np.array([robot.pos[1], robot.pos[0]]).astype('int'))
        return gradient_t

    def update_overall_gradient(self, gradient_t):
        # print(gradient_t)
        self.sensed_gradient += gradient_t

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
                edges.append((i, int(self.neighbors_table[i][j].id)))

        graph = ig.Graph(edges=edges)
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

    def draw_background(self, canvas):
        from PIL import ImageTk, Image
        if self.quantized_background is None:
            self.img = ImageTk.PhotoImage(Image.fromarray(np.uint8(self.background)))
        else:
            self.img = ImageTk.PhotoImage(Image.fromarray(np.uint8(self.quantized_background)))
        canvas.create_image(0, 0, image=self.img, anchor='nw')
