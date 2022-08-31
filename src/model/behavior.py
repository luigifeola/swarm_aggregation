from abc import ABC, abstractmethod
import numpy as np
from math import cos, radians, sin, exp
from helpers import random_walk as rw



class Behavior(ABC):

    def __init__(self):
        self.dr = np.array([0, 0]).astype('float64')  # maybe dr stands for direction
        self.color = "blue"

        self.crw_factor = 0.0
        self.levy_factor = 2.0
        self.std_motion_step = 1

    @abstractmethod
    def step(self, sensors, api):
        """Simulates 1 step of behavior (= 1 movement)"""

    def get_dr(self):
        return self.dr

    def get_rw_factors(self):
        return self.crw_factor, self.levy_factor, self.std_motion_step


class SocialBehavior(Behavior):

    def __init__(self):
        super().__init__()
        self.base_speed = 0

    def step(self, sensors, api):
        if self.base_speed == 0:
            self.base_speed = api.speed()

        self.dr[0], self.dr[1] = 0, 0
        self.update_behavior(sensors, api)

    def update_behavior(self, sensor, api):

        update_rate = 20
        if(api.get_tick()%update_rate == 0):
            # get local number of neighbours here
            neighbors_nbr = len(sensor["NEIGHBORS"])
            alpha = 1 #between 0 and 1
            beta = 0.3 #between 0 and +inf
            exp_factor = alpha * exp(-beta * neighbors_nbr)

            #Implementation 1 : exp_factor directly influence the RW factors + speed
            self.crw_factor = 0.9 * exp_factor
            self.levy_factor = 2 - 0.8 * exp_factor
            #taking speed into account ?

            api.set_speed(self.base_speed * exp_factor)

            #Implementation 2: exp_factor directly influence the RW factors + max_levy_steps
            # self.crw_factor = 0.9 * exp_factor
            # self.levy_factor = -0.8 * exp_factor + 2
            # self.max_levy_steps = int(1000 * exp_factor)
            # if(self.max_levy_steps == 0): self.max_levy_steps = 1

            #Implementation 3: exp_factor with probs
            # random_number = np.random.uniform(0,1)
            # if(random_number <= exp_factor):
            #     self.crw_factor = 0.9
            #     self.levy_factor = 1.2
            #     api.set_speed(self.base_speed)
            # else:
            #     self.crw_factor = 0
            #     self.levy_factor = 2
            #     api.set_speed(self.base_speed * exp_factor)

    def update_movement_based_on_state(self, sensors, api):
        turn_angle = api.get_turn_angle()
        self.dr = api.speed() * np.array([cos(radians(turn_angle)), sin(radians(turn_angle))])
        self.wall_avoidance(sensors)

    def wall_avoidance(self, sensors):
        if (sensors["FRONT"] and self.dr[0] >= 0) or (sensors["BACK"] and self.dr[0] <= 0):
            self.dr[0] = -self.dr[0]
        if (sensors["RIGHT"] and self.dr[1] <= 0) or (sensors["LEFT"] and self.dr[1] >= 0):
            self.dr[1] = -self.dr[1]


class DiffusiveBehavior(Behavior):

    def __init__(self, reset_jump):
        super().__init__()
        self.reset_jump = reset_jump
        self.gradient_memory = -1


    def step(self, sensors, api):
        self.update_behavior(sensors, api)

    def update_behavior(self, sensor, api):
        quantization_intervals = np.round(np.linspace(0.0, 1.0, num=api.get_perceptible_gradient.size + 1), 2)[1:]
        for idx, q in enumerate(quantization_intervals):
            if sensor['GRADIENT'] <= q:
                # print("sensor['GRADIENT']: ", sensor['GRADIENT'], '\t', 'val: ', q)

                # print("api.get_gradient: ", api.get_gradient(), '\t', 'api.get_perceptible_gradient[i]: ', api.get_perceptible_gradient[i])
                self.crw_factor = rw.get_crw_values(self.gradient_memory, idx)
                self.levy_factor = rw.get_levy_values(self.gradient_memory, idx)
                self.std_motion_step = rw.get_std_motion_steps_values(self.gradient_memory, idx)
                api.set_gradient(api.get_perceptible_gradient[idx])
                # api.reset_levy_counter()
                # print("Perceived a different gradient")

                self.gradient_memory = idx


                break

    def update_movement_based_on_state(self, sensors, api):
        turn_angle = api.get_turn_angle()
        # self.dr = api.speed() * np.array([cos(radians(turn_angle)), sin(radians(turn_angle))])
        self.dr = api.speed() * np.array([cos(turn_angle), sin(turn_angle)])
        wall_avoid = self.wall_avoidance(sensors)
        if self.reset_jump and wall_avoid:
            api.reset_levy_counter()

    def wall_avoidance(self, sensors):
        colliding = False
        if (sensors["RIGHT"] and self.dr[1] <= 0) or (sensors["LEFT"] and self.dr[1] >= 0):
            self.dr[1] = -self.dr[1]
            colliding = True
        if (sensors["FRONT"] and self.dr[0] >= 0) or (sensors["BACK"] and self.dr[0] <= 0):
            self.dr[0] = -self.dr[0]
            colliding = True

        return colliding

