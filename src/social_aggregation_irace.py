from controllers.main_controller import MainController, Configuration
from sys import argv
import os
import random
import numpy as np
import shutil

#best configs for 25 robots, 400x400, 10 000 steps
# Best configurations as commandlines (first number is the configuration ID; same order as above):
# 42  --t0 3 --t1 4 --a0 0.5593 --a1 1.5898 --a2 1.9601 --r0 0.6717 --r1 0.0101 --r2 0.0321
# 40  --t0 2 --t1 4 --a0 0.6932 --a1 1.4339 --a2 1.7877 --r0 0.8699 --r1 0.3781 --r2 0.1053
# 47  --t0 3 --t1 5 --a0 0.7697 --a1 1.835 --a2 1.9769 --r0 0.7645 --r1 0.4596 --r2 0.3857


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
    config_path = list_args[1]
    irace_config = config_path[:-4] + "_temp.txt"
    # print('list_args: ', list_args)
    shutil.copyfile(config_path, irace_config)

    array_str = "NEIGHBORS_THRESHOLDS=" + list_args[3] + "," + list_args[5] + "\n" + "LEVY_FACTORS=" + list_args[7] + "," + list_args[9] + "," + list_args[11] + "\n" + "CRW_FACTORS=" + list_args[13] + "," + list_args[15] + "," + list_args[17]
    with open(irace_config, "a") as file:
        file.write(array_str + '\n')

    return irace_config


if __name__ == '__main__':
    print(main())
