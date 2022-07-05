from math import cos, radians, pi
import numpy as np

# factors
__crw_weights = []
__levy_weights = []
__max_levy_steps = 1000

# possible combination of values depending on the environment
__crw_values = []
__levy_values = []
__max_straight_steps_values = []


def crw_pdf(thetas, crw_factor):
    res = []
    for t in thetas:
        num = (1 - crw_factor ** 2)
        denom = 2 * pi * (1 + crw_factor ** 2 - 2 * crw_factor * cos(radians(t)))
        f = 1
        if denom != 0:
            f = num / denom
        res.append(f)
    return res


def levy_pdf(max_steps, levy_factor):
    pdf = [step ** (-levy_factor - 1) for step in range(1, max_steps + 1)]
    return pdf


def set_parameters(crw_factor, levy_factor, max_levy_steps=1000):
    global __crw_weights, __levy_weights, __max_levy_steps
    thetas = np.arange(0, 360)
    __crw_weights = crw_pdf(thetas, crw_factor)
    __levy_weights = levy_pdf(max_levy_steps, levy_factor)
    __max_levy_steps = max_levy_steps


def init_values(crw_params, levy_params, max_straight_steps_params):
    global __crw_values, __levy_values, __max_straight_steps_values
    # __crw_values = np.linspace(0.0, 0.99, num=quantization_bits)
    # __levy_values = np.linspace(2.0, 1.2, num=quantization_bits)
    # __max_straight_steps_values = np.linspace(1, 1000, num=quantization_bits, dtype=int)

    __crw_values = np.array(crw_params, dtype=float)
    __levy_values = np.array(levy_params, dtype=float)
    __max_straight_steps_values = np.array(max_straight_steps_params, dtype=int)
    # print('crw_values ', __crw_values)
    # print('levy_values ', __levy_values)
    # print('max_levy_values ', __max_straight_steps_values)


def get_crw_weights():
    return __crw_weights


def get_levy_weights():
    return __levy_weights


def get_max_levy_steps():
    return __max_levy_steps


def get_crw_values(i):
    return __crw_values[i]


def get_levy_values(i):
    return __levy_values[i]


def get_max_straight_steps_values(i):
    return __max_straight_steps_values[i]
