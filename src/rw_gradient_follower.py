from controllers.main_controller import MainController, Configuration
from controllers.view_controller import ViewController
from multiprocessing import Process, cpu_count
from sys import argv
import os
import random
import numpy as np
import shutil


# linear 3 2k steps
# 8943 1 8943 /home/luigi/swarm_aggregation/config/fixed_lambda_quadratic.txt 3 --std 13 --a0 1.52 --r0 0.91 --a1 1.74 --r1 0.48 --a2 1.98 --r2 0.68 --a3 1.47 --r3 0.36 --a4 1.61 --r4 0.35 --a5 1.94 --r5 0.18 --a6 1.7 --r6 0.44 --a7 1.6 --r7 0.97 --a8 1.22 --r8 0.13


# linear 3 10k steps
# 15562 1 15562 /home/luigi/swarm_aggregation/config/fixed_lambda_linear.txt 3 --std 6 --a0 1.61 --r0 0.93 --a1 1.85 --r1 0.88 --a2 1.99 --r2 0.3 --a3 1.3 --r3 0.15 --a4 1.93 --r4 0.63 --a5 1.85 --r5 0.01 --a6 1.79 --r6 0.77 --a7 1.42 --r7 0.37 --a8 1.2 --r8 0.03
home_path = os.path.expanduser('~')

# TODO: pass the gradient_memory flag from the config
gradient_memory = True


def main():
    random.seed(argv[1])
    config_file = generate_config_file(argv[1:])
    config = Configuration(config_file=config_file)
    if config.parameters["VISUALIZE"] != 0:
        main_controller = MainController(config)
        _ = ViewController(main_controller,
                           config.parameters["WIDTH"],
                           config.parameters["HEIGHT"],
                           config.parameters["FPS"])

        overall_gradient = main_controller.get_overall_gradient() / \
                            config.parameters['NB_ROBOTS'] / \
                            config.parameters['SIMULATION_STEPS']
        print(f"Overall gradient {overall_gradient}")
    else:
        run(config)  # this is for single run
        os.remove(config_file)


def generate_config_file(list_args):
    # print('list_args: ', list_args)
    config_path = list_args[3]
    irace_config = home_path + "/swarm_aggregation/config/irace/irace_config" + list_args[0] + '_' + list_args[
        1] + '_' + list_args[2] + ".txt"
    # print('list_args: ', list_args)
    shutil.copyfile(config_path, irace_config)
    # print(list_args[2:])
    q_bits = list_args[4]
    if 'std' in list_args[5]:
        std = list_args[6]
    else:
        print(list_args[5], list_args[6])
        print("Error no std_motion_steps defined")
        std = ' '
        exit(1)

    with open(irace_config, "a") as file:
        q_bits_str = 'QUANTIZATION_BITS=' + q_bits
        std_str = 'STD_MOTION_STEPS='
        _values = int(q_bits) * int(q_bits) if gradient_memory else int(q_bits)
        for i in range(_values):
            std_str += std + ','

        file.write(q_bits_str + '\n')
        file.write(std_str[:-1] + '\n')

    reshape_args = np.array(list_args[7:]).reshape(-1, 2)
    num_param = reshape_args.shape[0] // _values
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

        array_str = param + str(values).replace(' [', '').replace('[', '').replace(']', '').replace(' ', ',') \
            .replace("'", "")

        with open(irace_config, "a") as file:
            file.write(array_str + '\n')

    return irace_config


def run_processes(config: Configuration):
    nb_runs = config.parameters["NB_RUNS"]
    nb_cores = cpu_count()
    print(f'number of cores {nb_cores}')

    process_table = [Process(target=run, args=(config,)) for i in range(nb_runs)]
    for batch in range(nb_runs // nb_cores):
        for batch_process in range(nb_cores):
            process_table[batch_process + batch * nb_cores].start()
            print(f"launched process {batch_process + batch * nb_cores}")
        for batch_process in range(nb_cores):
            process_table[batch_process + batch * nb_cores].join()
            print(f"joined process {batch_process + batch * nb_cores}")
    for batch_process in range(nb_runs % nb_cores):
        process_table[batch_process + nb_runs - nb_runs % nb_cores].start()
        print(f"launched process {batch_process + nb_runs - nb_runs % nb_cores}")
    for batch_process in range(nb_runs % nb_cores):
        process_table[batch_process + nb_runs - nb_runs % nb_cores].join()
        print(f"joined process {batch_process + nb_runs - nb_runs % nb_cores}")


def run(config):
    # random.seed(argv[1])
    controller = MainController(config)
    controller.start_simulation()
    gradientVAL_file = f"overall_gradient.txt"
    gradientPOS_file = f"center_gradient_positions.txt"
    filepath = f"../data"
    os.makedirs(filepath, exist_ok=True)
    with open(f"{filepath}/{gradientVAL_file}", "a") as file:
        file.write(f"{argv[1:]}: {controller.get_overall_gradient()}\n")
    with open(f"{filepath}/{gradientPOS_file}", "a") as file:
        file.write(f"{argv[1:]}: {controller.environment.center_gradient}\n")
    # print(f"Overall gradient for {config.parameters['NB_ROBOTS']} robots: "
    #       f"{controller.get_overall_gradient()}")
    overall_gradient = controller.get_overall_gradient() / \
                       config.parameters['NB_ROBOTS'] / \
                       config.parameters['SIMULATION_STEPS']
    print(f"{overall_gradient}")


if __name__ == '__main__':
    main()
