from enum import Enum
from abc import ABC, abstractmethod
import numpy as np
from math import cos, radians, sin
from helpers import random_walk as rw
from helpers.utils import rotate


class State(Enum):
    EXPLORING = 1
    INTENSE_LIGHT = 2
    DARK_LIGHT = 3


class Behavior(ABC):

    def __init__(self):
        self.dr = np.array([0, 0]).astype('float64')            # maybe dr stands for direction
        self.color = "blue"

    @abstractmethod
    def step(self, sensors, api):
        """Simulates 1 step of behavior (= 1 movement)"""

    def get_dr(self):
        return self.dr



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
        self.state = State.EXPLORING
        if sensor["GRADIENT"] < 0.6:
            # print('Brownian')
            self.state = State.DARK_LIGHT
            # self.max_levy_steps = 1
        else:
            # print('Levy')
            self.state = State.INTENSE_LIGHT
            # self.max_levy_steps = 1000

        for i, q in enumerate(api.get_perceptible_gradient):
            if sensor['GRADIENT'] <= q:
                self.crw_factor = rw.get_crw_values()[i]
                self.levy_factor = rw.get_levy_values()[i]
                self.max_levy_steps = rw.get_max_straight_steps_values()[i]
                break

    def get_rw_factors(self):
        return self.crw_factor, self.levy_factor, self.max_levy_steps

    def update_movement_based_on_state(self, sensors, api):
        turn_angle = api.get_levy_turn_angle()
        self.dr = api.speed() * np.array([cos(radians(turn_angle)), sin(radians(turn_angle))])
        if self.wall_avoidance(sensors):
            api.reset_levy_counter()

    def wall_avoidance(self, sensors):
        if (sensors["RIGHT"] and self.dr[1] <= 0) or (sensors["LEFT"] and self.dr[1] >= 0):
            self.dr[1] = -self.dr[1]
            return True
        elif (sensors["FRONT"] and self.dr[0] >= 0) or (sensors["BACK"] and self.dr[0] <= 0):
            self.dr[0] = -self.dr[0]
            # self.dr[0] = rotate(self.dr)
            return True
        return False


