from controllers.main_controller import MainController, Configuration
from controllers.view_controller import ViewController
from sys import argv
import os
import random
import numpy as np
import shutil

# sample args:
# 1033768854 /home/luigi/swarm_aggregation/config/config.txt --a0 1.3366 --r0 0.9068 --st0 439
# --a1 1.2363 --r1 0.2108 --st1 953
# --a2 1.4137 --r2 0.4494 --st2 390


def main():
    random.seed(argv[1])
    config_file = generate_config_file(argv[1:])
    # print('config_file: ', config_file)
    config = Configuration(config_file=config_file)
    gradient = run(config)
    # random.seed(argv[1])
    # config_file = generate_config_file(argv[1:])
    # config = Configuration(config_file=config_file)
    # main_controller = MainController(config)
    # _ = ViewController(main_controller,
    #                    config.parameters["WIDTH"],
    #                    config.parameters["HEIGHT"],
    #                    config.parameters["FPS"])

    # os.remove(config_file)
    # return main_controller.get_overall_gradient()
    return gradient



def run(config):
    controller = MainController(config)
    controller.start_simulation()
    # filename = "overall_gradient.txt"
    filepath = "/home/luigi/swarm_aggregation/data"
    os.makedirs(filepath, exist_ok=True)
    # with open(os.path.join(filepath, filename), "a") as file:
    #     file.write(str(controller.get_overall_gradient()) + '\n')
    # print(f"{controller.get_overall_gradient()}")
    return controller.get_overall_gradient()


def generate_config_file(list_args):

    config_path = list_args[1]
    irace_config = "/home/luigi/swarm_aggregation/config/irace_config"+list_args[0]+".txt"
    # print('list_args: ', list_args)
    shutil.copyfile(config_path, irace_config)
    # print(list_args[2:])
    reshape_args = np.array(list_args[2:]).reshape(-1, 2)
    for i in range(reshape_args.shape[0]//3):
        values = np.take(reshape_args[:, 1], [i, i + 3, i + 6])
        param = ''
        if 'r' in reshape_args[i, 0]:
            param = 'CRW_FACTORS='
        if 'a' in reshape_args[i, 0]:
            param = 'LEVY_FACTORS='
        if 'st' in reshape_args[i, 0]:
            param = 'MAX_STRAIGHT_STEPS='

        array_str = param+str(values).replace(' [', '').replace('[', '').replace(']', '').replace(' ', ',')\
                                                                                         .replace("'", "")

        with open(irace_config, "a") as file:
            file.write(array_str + '\n')


    return irace_config


if __name__ == '__main__':
    print(main())
