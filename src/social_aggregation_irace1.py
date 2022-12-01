from controllers.main_controller import MainController, Configuration
from sys import argv
import os
import random
import numpy as np
import shutil

def main():
    random.seed(argv[1])
    config_file = generate_config_file(argv[1:])
    config = Configuration(config_file=config_file)
    os.remove(config_file)
    metric = run(config)
    return metric

def run(config):
    controller = MainController(config)
    controller.start_simulation()
    return -controller.get_cluster_metric() #minus sign because irace is minimizing !

def generate_config_file(list_args):
    print('list_args: ', list_args)
    seed = list_args[0]
    config_id = list_args[1]
    instance_id = list_args[2]
    config_path = list_args[3]
    irace_config = config_path[:-4] + seed + config_id + instance_id +  "_temp.txt"
    # print('list_args: ', list_args)
    shutil.copyfile(config_path, irace_config)

    array_str = "NEIGHBORS_THRESHOLDS=" + list_args[5] + "," + list_args[7] + "\n" + "LEVY_FACTORS=" + list_args[9] + "," + list_args[11] + "," + list_args[13] + "\n" + "CRW_FACTORS=" + list_args[15] + "," + list_args[17] + "," + list_args[19]+ "\n" + "STD_MOTION_STEPS=" + list_args[21] + "," + list_args[21]+ "," + list_args[21]+ "\n" + "IRACE_SWITCH=1"

    with open(irace_config, "a") as file:
        file.write(array_str + '\n')

    return irace_config


if __name__ == '__main__':
    print(main())
