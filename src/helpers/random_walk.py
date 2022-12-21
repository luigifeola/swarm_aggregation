from math import cos, radians, pi
import numpy as np
import math


import random
from sys import argv
random.seed(int(argv[1]))

# possible combination of values depending on the environment

__crw_values_grad = np.array([])
__levy_values_grad = np.array([])
__std_motion_steps_values_grad = np.array([])
__crw_values_soc = np.array([])
__levy_values_soc = np.array([])
__std_motion_steps_values_soc = np.array([])
__neighbors_thresholds_values = np.array([])


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
def init_values(crw_params_grad, levy_params_grad, std_motion_steps_grad,
    crw_params_soc, levy_params_soc, std_motion_steps_soc, neighbors_thresholds, q_bits=-1):
    global __crw_values_grad, __levy_values_grad, __std_motion_steps_values_grad, __crw_values_soc, __levy_values_soc, __std_motion_steps_values_soc, __neighbors_thresholds_values

    __crw_values_grad = np.array(crw_params_grad, dtype=float)
    __levy_values_grad = np.array(levy_params_grad, dtype=float)
    __std_motion_steps_values_grad = np.array(std_motion_steps_grad, dtype=int)
    __crw_values_soc = np.array(crw_params_soc, dtype=float)
    __levy_values_soc = np.array(levy_params_soc, dtype=float)
    __std_motion_steps_values_soc = np.array(std_motion_steps_soc, dtype=int)
    __neighbors_thresholds_values = np.array(neighbors_thresholds, dtype=int)
    
    if q_bits != -1:
        __crw_values_grad = __crw_values_grad.reshape(q_bits, q_bits)
        __levy_values_grad = __levy_values_grad.reshape(q_bits, q_bits)
        __std_motion_steps_values_grad = __std_motion_steps_values_grad.reshape(q_bits, q_bits)

def get_crw_values_grad(i, f=-1):
    if f != -1:
        return __crw_values_grad[i][f]
    return __crw_values_grad[i]

def get_crw_values_soc(i):
    return __crw_values_soc[i]

def get_levy_values_grad(i, f=-1):
    if f != -1:
        return __levy_values_grad[i][f]
    return __levy_values_grad[i]

def get_levy_values_soc(i):
    return __levy_values_soc[i]

def get_std_motion_steps_values_grad(i, f=-1):
    if f != -1:
        return __std_motion_steps_values_grad[i][f]
    return __std_motion_steps_values_grad[i]

def get_std_motion_steps_values_soc(i):
    return __std_motion_steps_values_soc[i]

def get_neighbors_thresholds_values():
    return __neighbors_thresholds_values
