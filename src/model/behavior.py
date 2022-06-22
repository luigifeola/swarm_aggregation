from enum import Enum
from abc import ABC, abstractmethod
import numpy as np
from math import cos, radians, sin
from helpers.utils import get_orientation_from_vector, norm

DIFFERENT_PERCEPTION_NUMBER = 3


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

        self.crw_factor = 0.0
        self.levy_factor = 2.0
        self.max_levy_steps = 1000

        self.gradient_perceptible = []
        self.crw_values = []
        self.levy_values = []
        self.max_levy_values = []
        self.init_values()

    def init_values(self):
        # TODO: here you should load the DIFFERENT_PERCEPTION_NUMBER from the config or from the agent
        # TODO: maybe could be global in the random_walk.py
        self.gradient_perceptible = np.linspace(0.2, 1.0, num=DIFFERENT_PERCEPTION_NUMBER)
        self.crw_values = np.linspace(0.0, 0.99, num=DIFFERENT_PERCEPTION_NUMBER)
        self.levy_values = np.linspace(2.0, 1.2, num=DIFFERENT_PERCEPTION_NUMBER)
        self.max_levy_values = np.linspace(1, 1000, num=DIFFERENT_PERCEPTION_NUMBER, dtype=int)
        print('gradient_perceptible ', self.gradient_perceptible)
        print('crw_values ', self.crw_values)
        print('levy_values ', self.levy_values)
        print('max_levy_values ', self.max_levy_values)


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
            # self.crw_factor = 0.99 * (sensor["GRADIENT"])
            # self.levy_factor = -0.8 * (sensor["GRADIENT"]) + 2

        for i, q in enumerate(self.gradient_perceptible):
            if sensor['GRADIENT'] <= q:
                self.crw_factor = self.crw_values[i]
                self.levy_factor = self.levy_values[i]
                self.max_levy_steps = self.max_levy_values[i]
                break

    def get_rw_factors(self):
        return self.crw_factor, self.levy_factor, self.max_levy_steps

    def update_movement_based_on_state(self, sensors, api):
        turn_angle = api.get_levy_turn_angle()
        self.dr = api.speed() * np.array([cos(radians(turn_angle)), sin(radians(turn_angle))])
        if self.wall_avoidance(sensors):
            api.reset_levy_counter()

    def wall_avoidance(self, sensors):
        if (sensors["FRONT"] and self.dr[0] >= 0) or (sensors["BACK"] and self.dr[0] <= 0):
            self.dr[0] = -self.dr[0]
            return True
        if (sensors["RIGHT"] and self.dr[1] <= 0) or (sensors["LEFT"] and self.dr[1] >= 0):
            self.dr[1] = -self.dr[1]
            return True
        return False


