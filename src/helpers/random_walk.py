from math import cos, radians, pi
import numpy as np

__crw_weights = []
__levy_weights = []
__max_levy_steps = 1000


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
    global __crw_weights, __levy_weights
    thetas = np.arange(0, 360)
    __crw_weights = crw_pdf(thetas, crw_factor)
    __levy_weights = levy_pdf(max_levy_steps, levy_factor)


def get_crw_weights():
    return __crw_weights


def get_levy_weights():
    return __levy_weights


def get_max_levy_steps():
    return __max_levy_steps
