import math

from helpers import random_walk as rw
import random
from math import sin, cos, radians
from collections import deque

import numpy as np

from helpers.utils import get_orientation_from_vector, rotate, rgb


class AgentAPI:
    def __init__(self, agent):
        self.speed = agent.speed
        self.radius = agent.radius
        self.get_turn_angle = agent.get_turn_angle
        self.reset_levy_counter = agent.reset_levy_counter
        self.get_mu = agent.noise_mu
        self.get_perceptible_gradient = agent.environment.get_perceptible_gradient()
        self.set_gradient = agent.set_gradient
        self.get_gradient = agent.get_gradient
        self.get_tick = agent.get_tick
        self.pos = agent.pos
        self.set_speed = agent.set_speed
        self.stop_exploration = agent.stop_exploration
        self.resume_exploration = agent.resume_exploration


class Agent:

    def __init__(self, robot_id, x, y, speed, radius,
                 bool_noise, noise_mu, noise_musd, noise_sd,
                 behavior, environment):

        self.id = robot_id
        self.pos = np.array([x, y]).astype('float64')
        self._speed = speed
        self.max_speed = speed
        self._radius = radius
        self.orientation = random.random() * 360  # 360 degree angle

        self.bool_noise = bool_noise
        self.noise_mu = random.gauss(noise_mu, noise_musd)
        if random.random() >= 0.5:
            self.noise_mu = -self.noise_mu
        self.noise_sd = noise_sd

        self.environment = environment

        self.levy_factor = 2.0
        self.std_motion_step = 10
        self.crw_factor = 0.0
        self.max_levy_steps = 1000

        self.gradient = 0

        self.levy_counter = 1
        self.trace = deque(self.pos, maxlen=100)

        self.behavior = behavior
        self.api = AgentAPI(self)

        self.tick = 0

    def __str__(self):
        return f"ID: {self.id}\n" \
               f"drift: {round(self.noise_mu, 5)}\n" \
               f"position: {np.round(self.pos, 2)}\n" \
               f"angle: {np.round(self.orientation, 2)}\n" \
               f"dr: {self.behavior.get_dr()}\n" \
               f"rho: {np.round(self.behavior.get_rw_factors()[0], 2)}\n" \
               f"alpha: {np.round(self.behavior.get_rw_factors()[1], 2)}\n" \
               f"lambda: {np.round(self.behavior.get_rw_factors()[2], 2)}\n" \
               f"straight counter: {self.levy_counter}\n" \
               f"perceived gradient [0 - 1]: {self.gradient}\n" \
               f"real gradient [0 - 1]: {np.round(self.environment.sense_gradient(self), 2)}\n" \
               f"neighbors: {self.environment.sense_neighbors(self)}"

    def __repr__(self):
        return f"bot {self.id}"

    def step(self):
        sensors = self.environment.get_sensors(self)

        # set the walk parameters based on the sensed gradient
        self.behavior.step(sensors, AgentAPI(self))

        [self.crw_factor, self.levy_factor, self.std_motion_step] = self.behavior.get_rw_factors()

        self.behavior.update_movement_based_on_state(sensors, AgentAPI(self))
        self.move()
        self.update_trace()
        self.tick += 1
        self.environment.update_overall_gradient(self.gradient)

    def update_trace(self):
        self.trace.appendleft(self.pos[1])
        self.trace.appendleft(self.pos[0])

    def move(self):
        wanted_movement = rotate(self.behavior.get_dr(), self.orientation)
        if self.bool_noise:
            noise_angle = random.gauss(self.noise_mu, self.noise_sd)
            noisy_movement = rotate(wanted_movement, noise_angle)
            self.orientation = get_orientation_from_vector(noisy_movement)
            self.pos = self.clamp_to_map(self.pos + noisy_movement)
        else:
            self.orientation = get_orientation_from_vector(wanted_movement)
            self.pos = self.clamp_to_map(self.pos + wanted_movement)

    def clamp_to_map(self, new_position):
        if new_position[0] < self._radius:
            new_position[0] = self._radius
        if new_position[1] < self._radius:
            new_position[1] = self._radius
        if new_position[0] > self.environment.width - self._radius:
            new_position[0] = self.environment.width - self._radius
        if new_position[1] > self.environment.height - self._radius:
            new_position[1] = self.environment.height - self._radius
        return new_position

    def update_levy_counter(self):
        self.levy_counter -= 1

        if self.levy_counter <= 0:
            self.levy_counter = round(math.fabs(rw.levy_distribution(self.std_motion_step, self.levy_factor)))


    def set_gradient(self, gradient):
        self.gradient = gradient

    def get_gradient(self):
        return self.gradient

    def get_turn_angle(self):
        angle = 0
        if self.levy_counter <= 1:
            angle = math.fabs(rw.wrapped_cauchy_ppf(self.crw_factor))
        self.update_levy_counter()
        return angle

    def reset_levy_counter(self):
        self.levy_counter = 1

    def get_tick(self):
        return self.tick

    def draw(self, canvas, draw_trace_debug, draw_communication_debug):
        mid_val = int(255 - self.gradient*255)
        outline_col = rgb(mid_val, mid_val, 0)
        circle = canvas.create_oval(self.pos[0] - self._radius,
                                    self.pos[1] - self._radius,
                                    self.pos[0] + self._radius,
                                    self.pos[1] + self._radius,
                                    fill=self.behavior.color,
                                    # fill=outline_col,
                                    outline=outline_col,   # self.colors[self.behavior.state],
                                    width=4)

        self.draw_orientation(canvas)
        if draw_trace_debug:
            self.draw_trace(canvas)
        if draw_communication_debug:
            self.draw_comm_radius(canvas)

    def draw_trace(self, canvas):
        tail = canvas.create_line(*self.trace, fill="green", width=5)

    def draw_comm_radius(self, canvas):
        circle = canvas.create_oval(self.pos[0] - self.environment.robot_communication_radius,
                                    self.pos[1] - self.environment.robot_communication_radius,
                                    self.pos[0] + self.environment.robot_communication_radius,
                                    self.pos[1] + self.environment.robot_communication_radius,
                                    outline="gray")

    def draw_orientation(self, canvas):
        line = canvas.create_line(self.pos[0],
                                  self.pos[1],
                                  self.pos[0] + self._radius * cos(radians(self.orientation)),
                                  self.pos[1] + self._radius * sin(radians(self.orientation)),
                                  fill="white")

    def speed(self):
        return self._speed

    def set_speed(self, speed):
        self._speed = speed

    def stop_exploration(self):
        self._speed = 0

    def resume_exploration(self):
        self._speed = self.max_speed

    def radius(self):
        return self._radius
