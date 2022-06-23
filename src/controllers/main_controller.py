from helpers import random_walk
from model.environment import Environment


class Configuration:
    def __init__(self, config_file):
        self.parameters = dict()
        self.read_config(config_file)

    def read_config(self, config_file):
        with open(config_file, "r") as file:
            for line in file:
                args = line.strip().split("=")
                parameter = args[0]
                value = args[1]
                self.add_to_parameters(parameter, value)

    def add_to_parameters(self, parameter, value):
        float_params = {"CRW_FACTOR", "ROBOT_SPEED", "LEVY_FACTOR", "NOISE_MU", "NOISE_MUSD",
                        "NOISE_SD", "COMMUNICATION_RADIUS"}
        if parameter in float_params:
            self.parameters[parameter] = float(value)
        else:
            self.parameters[parameter] = int(value)


class MainController:

    def __init__(self, config: Configuration):
        self.config = config
        self.environment = Environment(width=self.config.parameters["WIDTH"],
                                       height=self.config.parameters["HEIGHT"],
                                       nb_robots=self.config.parameters["NB_ROBOTS"],
                                       robot_speed=self.config.parameters["ROBOT_SPEED"],
                                       communication_radius=self.config.parameters["COMMUNICATION_RADIUS"],
                                       robot_radius=self.config.parameters["ROBOT_RADIUS"],
                                       quantization_bits=config.parameters["QUANTIZATION_BITS"],
                                       bool_noise=self.config.parameters["NOISE_FLAG"],
                                       noise_mu=self.config.parameters["NOISE_MU"],
                                       noise_musd=self.config.parameters["NOISE_MUSD"],
                                       noise_sd=self.config.parameters["NOISE_SD"]
                                       )
        self.tick = 0

    def step(self):
        if self.tick < self.config.parameters["SIMULATION_STEPS"]:
            self.tick += 1
            self.environment.step()
            # print(f"Overall gradient for {self.config.parameters['NB_ROBOTS']} robots: "
            #       f"{self.get_overall_gradient()}")

    def start_simulation(self):
        # now = time.time()
        for step_nb in range(self.config.parameters["SIMULATION_STEPS"]):
            self.step()
        # print(f"Overall gradient for {self.config.parameters['NB_ROBOTS']} robots: "
        #       f"{self.get_overall_gradient()}")
        # print(f"Time taken for {self.config.p-arameters['SIMULATION_STEPS']} steps: {time.time()-now}")
        # print(f"Time taken for {self.config.parameters['SIMULATION_STEPS']} steps: {time.time()-now}")

    def get_robot_at(self, x, y):
        return self.environment.get_robot_at(x, y)

    def get_overall_gradient(self):
        return self.environment.sensed_gradient

    def write_metrics(self, file_path):
        print("Writing in %s" % file_path)
        with open(file_path, 'w') as f:
            for line in self.environment.metrics:
                f.write(line)
                f.write('\n')
