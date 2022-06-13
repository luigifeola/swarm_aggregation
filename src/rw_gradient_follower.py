from controllers.main_controller import MainController, Configuration
from controllers.view_controller import ViewController
from multiprocessing import Process, cpu_count
from sys import argv
import os


def main():
    config = Configuration(config_file=argv[1])
    if config.parameters["VISUALIZE"] != 0:
        main_controller = MainController(config)
        _ = ViewController(main_controller,
                           config.parameters["WIDTH"],
                           config.parameters["HEIGHT"],
                           config.parameters["FPS"])
    else:
        for arg in argv[1:]:
            config = Configuration(config_file=arg)
            run_processes(config)


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


if __name__ == '__main__':
    main()
