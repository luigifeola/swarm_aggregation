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
    os.remove(config_file)
    gradient = run(config)
    return gradient



def run(config):
    controller = MainController(config)
    controller.start_simulation()
    gradientVAL_file = f"overall_gradient.txt"
    gradientPOS_file = f"center_gradient_positions.txt"
    filepath = f"{home_path}/swarm_aggregation/data"
    os.makedirs(filepath, exist_ok=True)
    with open(f"{filepath}/{gradientVAL_file}", "a") as file:
        file.write(f"{argv[1:]}: {controller.get_overall_gradient()}\n")
    with open(f"{filepath}/{gradientPOS_file}", "a") as file:
        file.write(f"{argv[1:]}: {controller.environment.center_gradient}\n")
    return controller.get_overall_gradient()


def generate_config_file(list_args):
    # print('list_args: ', list_args)
    config_path = list_args[3]
    irace_config = home_path+"/swarm_aggregation/config/irace/irace_config"+list_args[0]+'_'+list_args[1]+'_'+list_args[2]+".txt"
    # print('list_args: ', list_args)
    shutil.copyfile(config_path, irace_config)
    # print(list_args[2:])
    q_bits = list_args[4]
    if 'std' in list_args[5]:
        std = list_args[6]
    else:
        print(list_args[5], list_args[6])
        print("Error no std_motion_steps defined")
        exit(1)

    with open(irace_config, "a") as file:
        q_bits_str = 'QUANTIZATION_BITS='+q_bits
        std_str = 'STD_MOTION_STEPS='
        for i in range(int(q_bits)):
            std_str += std + ','
        file.write(q_bits_str + '\n')
        file.write(std_str[:-1] + '\n')

    reshape_args = np.array(list_args[7:]).reshape(-1, 2)
    num_param = reshape_args.shape[0]//int(q_bits)
    for i in range(num_param):
        idxs = np.arange(i, reshape_args.shape[0], num_param)
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
