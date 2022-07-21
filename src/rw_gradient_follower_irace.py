from controllers.main_controller import MainController, Configuration
from sys import argv
import os
import random
import numpy as np
import shutil

home_path = os.path.expanduser('~')


def main():
    random.seed(argv[1])
    config_file = generate_config_file(argv[1:])
    config = Configuration(config_file=config_file)
    gradient = run(config)
    os.remove(config_file)
    return gradient



def run(config):
    controller = MainController(config)
    controller.start_simulation()
    # filename = "overall_gradient.txt"
    filepath = home_path+"/swarm_aggregation/data"
    os.makedirs(filepath, exist_ok=True)
    # with open(os.path.join(filepath, filename), "a") as file:
    #     file.write(str(controller.get_overall_gradient()) + '\n')
    # print(f"{controller.get_overall_gradient()}")
    return controller.get_overall_gradient()


def generate_config_file(list_args):

    config_path = list_args[3]
    irace_config = home_path+"/swarm_aggregation/config/irace/irace_config"+list_args[0]+'_'+list_args[1]+'_'+list_args[2]+".txt"
    # print('list_args: ', list_args)
    shutil.copyfile(config_path, irace_config)
    # print(list_args[2:])
    q_bits = list_args[4]

    with open(irace_config, "a") as file:
        q_bits_str = 'QUANTIZATION_BITS='+str(q_bits)
        file.write(q_bits_str + '\n')

    reshape_args = np.array(list_args[5:]).reshape(-1, 2)
    for i in range(reshape_args.shape[0]//int(q_bits)):
        idxs = np.arange(i, reshape_args.shape[0], 3)
        values = np.take(reshape_args[:, 1], idxs)
        param = ''
        if 'r' in reshape_args[i, 0]:
            param = 'CRW_FACTORS='
        if 'a' in reshape_args[i, 0]:
            param = 'LEVY_FACTORS='
        if 'st' in reshape_args[i, 0]:
            param = 'STD_MOTION_STEPS='

        array_str = param+str(values).replace(' [', '').replace('[', '').replace(']', '').replace(' ', ',')\
                                                                                         .replace("'", "")

        with open(irace_config, "a") as file:
            file.write(array_str + '\n')

    return irace_config


if __name__ == '__main__':
    print(main())
