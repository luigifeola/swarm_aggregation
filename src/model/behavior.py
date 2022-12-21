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

    def __init__(self, reset_jump):
        super().__init__()
        self.base_speed = 0
        self.reset_jump = reset_jump
        self.index = 0

    def step(self, sensors, api):
        if self.base_speed == 0:
            self.base_speed = api.speed()

        self.dr[0], self.dr[1] = 0, 0
        self.update_behavior(sensors, api)

    def update_behavior(self, sensor, api):

        # get local number of neighbours here
        neighbors_nbr = len(sensor["NEIGHBORS"])

        if(api.get_irace_switch() == 1):
            # Implementation with discretization and thresholds
            self.index = 0
            for threshold in rw.get_neighbors_thresholds_values():
                if(neighbors_nbr >= threshold):
                    self.index+=1

            self.crw_factor = rw.get_crw_values_soc(self.index)
            self.levy_factor = rw.get_levy_values_soc(self.index)
            self.std_motion_step = rw.get_std_motion_steps_values_soc(self.index)

        if(api.get_irace_switch() == 2):
            #Implementation with only 2 RW states
            self.std_motion_step = rw.get_std_motion_steps_values_soc(0)
            if(self.index == 0):
                self.crw_factor = rw.get_crw_values_soc(self.index)
                self.levy_factor = rw.get_levy_values_soc(self.index)
                if(neighbors_nbr >= rw.get_neighbors_thresholds_values()[0]):
                    self.index = 1
            elif(self.index == 1):
                self.crw_factor = rw.get_crw_values_soc(self.index)
                self.levy_factor = rw.get_levy_values_soc(self.index)
                if(neighbors_nbr < rw.get_neighbors_thresholds_values()[1]):
                    self.index = 0
        #part to compute gradient metric correctly if heterogeneous swarm              
        quantization_intervals = np.round(np.linspace(0.0, 1.0, num=api.get_perceptible_gradient.size + 1), 2)[1:]

        previous_idx = api.get_previous_bin()
        idx = np.digitize(sensor['GRADIENT'], quantization_intervals, right=True)

        if api.get_levy_counter() <= 1 or (previous_idx != idx and api.instant_sensing):
            # print(f"sensor['GRADIENT']: {sensor['GRADIENT']}")
            api.set_gradient(api.get_perceptible_gradient[idx])
            # print(f"previous idx:{previous_idx}, actual idx:{idx}")
            api.set_previous_bin(idx)


    def update_movement_based_on_state(self, sensors, api):
        turn_angle = api.get_turn_angle()
        self.dr = api.speed() * np.array([cos(turn_angle), sin(turn_angle)])
        if self.reset_jump and self.wall_avoidance(sensors):
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


class DiffusiveBehavior(Behavior):

    def __init__(self, reset_jump):
        super().__init__()
        self.reset_jump = reset_jump


    def step(self, sensors, api):
        self.dr[0], self.dr[1] = 0, 0
        self.update_behavior(sensors, api)

    def update_behavior(self, sensor, api):
        quantization_intervals = np.round(np.linspace(0.0, 1.0, num=api.get_perceptible_gradient.size + 1), 2)[1:]

        previous_idx = api.get_previous_bin()
        idx = np.digitize(sensor['GRADIENT'], quantization_intervals, right=True)

        if api.get_levy_counter() <= 1 or (previous_idx != idx and api.instant_sensing):
            # print(f"sensor['GRADIENT']: {sensor['GRADIENT']}")
            self.crw_factor = rw.get_crw_values_grad(idx)
            self.levy_factor = rw.get_levy_values_grad(idx)
            self.std_motion_step = rw.get_std_motion_steps_values_grad(idx)
            api.set_gradient(api.get_perceptible_gradient[idx])
            # print(f"previous idx:{previous_idx}, actual idx:{idx}")
            if previous_idx != idx and api.instant_sensing:
                api.reset_levy_counter()
                print(f"{api.get_id()} - Perceived a different gradient")

            api.set_previous_bin(idx)


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
