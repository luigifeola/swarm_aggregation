from math import atan2, pi, radians
import numpy as np


def norm(vector):
    return (sum(x ** 2 for x in vector)) ** 0.5


def get_orientation_from_vector(vector):
    angle = atan2(vector[1], vector[0])
    return (360 * angle / (2 * pi)) % 360


def rotation_matrix(angle):
    theta = radians(angle)
    return np.array(((np.cos(theta), -np.sin(theta)),
                     (np.sin(theta), np.cos(theta))))


def rotate(vector, angle):
    rot_mat = rotation_matrix(angle)
    rotated_vector = rot_mat.dot(vector)
    return rotated_vector


def distance_between(robot1, robot2):
    return norm(robot2.pos - robot1.pos)


def matrix_index_distances(mat, index):
    i, j = np.indices(mat.shape, sparse=True)
    return np.sqrt((i - index[0]) ** 2 + (j - index[1]) ** 2)


# Define a function for filling the rectangle with random colors
def rgb(r, g, b):
    return "#%s%s%s" % tuple([hex(c)[2:].rjust(2, "0")
                              for c in (r, g, b)])


def get_pixel_col(np_img, pixel):
    return np_img[pixel[0], pixel[1]] / 255
    # return round(np_img[pixel[0], pixel[1]] / 255, 4)


