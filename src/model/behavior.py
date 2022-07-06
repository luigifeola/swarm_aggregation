from enum import Enum
from abc import ABC, abstractmethod
import numpy as np
from math import cos, radians, sin, exp
from helpers.utils import get_orientation_from_vector, norm
from helpers import random_walk as rw
from helpers.utils import rotate
from random import randint


class State(Enum):
    EXPLORING = 1
    RESTING = 2


class Behavior(ABC):

    def __init__(self):
        self.dr = np.array([0, 0]).astype('float64')  # maybe dr stands for direction
        self.color = "blue"

    @abstractmethod
    def step(self, sensors, api):
        """Simulates 1 step of behavior (= 1 movement)"""

    def get_dr(self):
        return self.dr

    def get_rw_factors(self):
        return self.crw_factor, self.levy_factor, self.max_levy_steps


class SocialBehavior(Behavior):

    def __init__(self):
        super().__init__()

        self.crw_factor = 0.0
        self.levy_factor = 2.0

        # TODO: maybe use max_levy_steps instead of modifying the velocity
        self.max_levy_steps = 1000

        self.base_speed = 0

    def step(self, sensors, api):
        if self.base_speed == 0:
            self.base_speed = api.speed()

        self.dr[0], self.dr[1] = 0, 0
        self.update_behavior(sensors, api)

    def update_behavior(self, sensor, api):

        update_rate = 10
        if api.get_tick() % update_rate == 0:
            # get local number of neighbours here
            neighbors_nbr = len(sensor["NEIGHBORS"])
            alpha = 1  # between 0 and 1
            beta = 0.2  # between 0 and +inf
            exp_factor = alpha * exp(-beta * neighbors_nbr)
            self.crw_factor = 0.99 * exp_factor
            self.levy_factor = -0.8 * exp_factor + 2
            # taking speed into account ?
            api.set_speed(self.base_speed * exp_factor)

    def update_movement_based_on_state(self, sensors, api):
        turn_angle = api.get_levy_turn_angle()
        self.dr = api.speed() * np.array([cos(radians(turn_angle)), sin(radians(turn_angle))])
        self.wall_avoidance(sensors)

    def wall_avoidance(self, sensors):
        if (sensors["FRONT"] and self.dr[0] >= 0) or (sensors["BACK"] and self.dr[0] <= 0):
            self.dr[0] = -self.dr[0]
        if (sensors["RIGHT"] and self.dr[1] <= 0) or (sensors["LEFT"] and self.dr[1] >= 0):
            self.dr[1] = -self.dr[1]


class DiffusiveBehavior(Behavior):

    def __init__(self):
        super().__init__()

        self.state = State.EXPLORING

        self.crw_factor = 0.5
        self.levy_factor = 1.5
        self.max_levy_steps = 1000

    def step(self, sensors, api):
        self.dr[0], self.dr[1] = 0, 0
        self.update_behavior(sensors, api)

    def update_behavior(self, sensor, api):
        quantization_intervals = np.round(np.linspace(0.0, 1.0, num=api.get_perceptible_gradient.size + 1), 2)[1:]
        for i, q in enumerate(quantization_intervals):
            if sensor['GRADIENT'] <= q:
                # print("sensor['GRADIENT']: ", sensor['GRADIENT'], '\t', 'val: ', q)
                if api.get_gradient() != api.get_perceptible_gradient[i]:
                    # print("api.get_gradient: ", api.get_gradient(), '\t', 'api.get_perceptible_gradient[i]: ', api.get_perceptible_gradient[i])
                    self.crw_factor = rw.get_crw_values(i)
                    self.levy_factor = rw.get_levy_values(i)
                    self.max_levy_steps = rw.get_max_straight_steps_values(i)
                    api.set_gradient(api.get_perceptible_gradient[i])
                    # api.reset_levy_counter()
                    # print("Perceived a different gradient")
                break

    def update_movement_based_on_state(self, sensors, api):
        turn_angle = api.get_levy_turn_angle()
        self.dr = api.speed() * np.array([cos(radians(turn_angle)), sin(radians(turn_angle))])
        if self.wall_avoidance(sensors):
            api.reset_levy_counter()

    def wall_avoidance(self, sensors):
        if (sensors["RIGHT"] and self.dr[1] <= 0) or (sensors["LEFT"] and self.dr[1] >= 0):
            self.dr[1] = -self.dr[1]
            return True
        if (sensors["FRONT"] and self.dr[0] >= 0) or (sensors["BACK"] and self.dr[0] <= 0):
            self.dr[0] = -self.dr[0]
            # self.dr[0] = rotate(self.dr)
            return True
        return False
