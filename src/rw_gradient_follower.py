from controllers.main_controller import MainController, Configuration
from controllers.view_controller import ViewController
from multiprocessing import Process, cpu_count
from sys import argv
import os
import random
import numpy as np
import shutil


# to run the best result from irace with 3 quantization bits:
# 6515485 1 1 /home/luigi/swarm_aggregation/config/config_batch.txt 3 --a0 1.9689 --r0 0.606 --st0 1 --a1 1.3391 --r1 0.3714 --st1 389 --a2 1.2121 --r2 0.8337 --st2 948
## 6515485 1 1 /home/luigi/swarm_aggregation/config/config_batch.txt 4 --a0 1.9353 --r0 0.1620 --st0 503 --a1 1.966 --r1 0.27 --st1 762 --a2 1.218 --r2 0.3619 --st2 135 --a3 1.2229 --r3 0.8927 --st3 352

# alpha0   rho0 str_steps0 alpha1   rho1 str_steps1 alpha2   rho2 str_steps2 alpha3   rho3 str_steps3
# 1.9353 0.1620        503 1.9660 0.0270        762 1.2184 0.3619        135 1.2229 0.8927        352


home_path = os.path.expanduser('~')

# TODO: pass the gradient_memory flag from the config
gradient_memory = False


def main():
    random.seed(argv[1])
    if os.path.exists(argv[2]):
        # print("Config file exists")
        config_file = 'None'
        config = Configuration(config_file=argv[2])
    else:
        # print("Config file NOT exists")
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
        if config.parameters["NB_RUNS"] > 1:
            print(f"Running {config.parameters['NB_RUNS']} runs")
            run_processes(config)
        else:
            run(config)  # this is for single run
            if os.path.exists(config_file):
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
    controller = MainController(config)
    controller.start_simulation()
    gradientVAL_file = f"overall_gradient.txt"
    gradientPOS_file = f"center_gradient_positions.txt"
    filepath = f"../data"
    os.makedirs(filepath, exist_ok=True)
    overall_gradient = controller.get_overall_gradient() / \
                       config.parameters['NB_ROBOTS'] / \
                       config.parameters['SIMULATION_STEPS']
    with open(f"{filepath}/{gradientVAL_file}", "a") as file:
        # print(f"Writing on file: {filepath}/{gradientVAL_file}")
        file.write(f"{overall_gradient}\n")
    with open(f"{filepath}/{gradientPOS_file}", "a") as file:
        # print(f"Writing on file: {filepath}/{gradientPOS_file}")
        file.write(f"{controller.environment.center_gradient}\n")
    # print(f"Overall gradient for {config.parameters['NB_ROBOTS']} robots: "
    #       f"{controller.get_overall_gradient()}")
    print(f"{overall_gradient}")


if __name__ == '__main__':
    main()
