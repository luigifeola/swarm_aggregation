from math import cos, radians, pi
import numpy as np
import math


import random
from sys import argv
random.seed(int(argv[1]))

# possible combination of values depending on the environment
__crw_values = []
__levy_values = []
__std_motion_steps_values = []


def exponential_distribution(lambda_):
    u = random.uniform(0.0, 1.0)
    x = -lambda_ * math.log(1 - u)
    return x


def levy_distribution(std, alpha):
    u = math.pi * (random.uniform(0.0, 1.0) - 0.5)

    # Cauchy case
    if alpha == 1.0:
        t = math.tan(u)
        return std * t

    v = 0
    while v == 0:
        v = exponential_distribution(1.0)

    # Gaussian case
    if alpha == 2:
        t = 2 * math.sin(u) * math.sqrt(v)
        return std * t

    # General case
    t = math.sin(alpha * u) / math.pow(math.cos(u), 1 / alpha)
    s = math.pow(math.cos((1 - alpha) * u), 1 - alpha / alpha)

    return std * t * s


def wrapped_cauchy_ppf(crw_exponent):
    if crw_exponent == 0:
        return random.uniform(0.0, math.pi)

    q = 0.5
    u = random.uniform(0.0, 1.0)
    val = (1.0 - crw_exponent) / (1.0 + crw_exponent)
    theta = 2 * math.atan(val * math.tan(math.pi * (u - q)))
    return theta


# Here you initialize the different parameteres loaded from the config file
def init_values(crw_params, levy_params, std_motion_steps):
    global __crw_values, __levy_values, __std_motion_steps_values

    __crw_values = np.array(crw_params, dtype=float)
    __levy_values = np.array(levy_params, dtype=float)
    __std_motion_steps_values = np.array(std_motion_steps, dtype=int)
    # print('crw_values ', __crw_values)
    # print('levy_values ', __levy_values)
    # print('max_levy_values ', __std_motion_steps_values)


def get_crw_values(i):
    return __crw_values[i]


def get_levy_values(i):
    return __levy_values[i]


def get_std_motion_steps_values(i):
    return __std_motion_steps_values[i]
