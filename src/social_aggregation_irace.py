from controllers.main_controller import MainController, Configuration
from sys import argv
import os
import random
import numpy as np
import shutil

#best configs for 25 robots, 400x400, 10 000 steps, 300 exp
# Best configurations as commandlines (first number is the configuration ID; same order as above):
# 42  --t0 3 --t1 4 --a0 0.5593 --a1 1.5898 --a2 1.9601 --r0 0.6717 --r1 0.0101 --r2 0.0321
# 40  --t0 2 --t1 4 --a0 0.6932 --a1 1.4339 --a2 1.7877 --r0 0.8699 --r1 0.3781 --r2 0.1053
# 47  --t0 3 --t1 5 --a0 0.7697 --a1 1.835 --a2 1.9769 --r0 0.7645 --r1 0.4596 --r2 0.3857

#best configs for 25 robots, 400x400, 3000 steps, 300 exp => less good results, culminate at 0.5 cluster metric
# Best configurations (first number is the configuration ID; listed from best to worst according to the sum of ranks):
#    t0 t1     a0     a1     a2     r0     r1     r2
# 43  2  6 0.5707 1.9715 1.9660 0.9574 0.2778 0.0875
# 38  2  8 0.5468 1.9944 1.5856 0.0661 0.1856 0.4123
# 28  2  5 0.6802 1.9745 1.8158 0.7661 0.2771 0.0966
# 1   2  4 0.8000 1.4000 2.0000 0.9000 0.4000 0.0000
# 36  3  5 0.9336 1.9431 1.8442 0.7919 0.4219 0.2546

#best configs for 25 robots, 400x400, 10 000 steps, 10 000 exp
# Best configurations (first number is the configuration ID; listed from best to worst according to the sum of ranks):
#      t0 t1     a0     a1     a2     r0     r1     r2
# 1173  2  3 0.5764 0.7083 1.9955 0.6377 0.6851 0.0593
# 1166  2  3 0.5182 0.6124 1.9458 0.8070 0.8154 0.0192
# 1043  2  3 0.5744 0.7354 1.9460 0.5386 0.6152 0.0742
# 1170  2  3 0.5870 0.9794 1.9426 0.5718 0.7463 0.0585
# 974   2  3 0.5337 0.6972 1.9444 0.5876 0.7119 0.1077

#best configs for 25 robots, 400x400, 5000 steps, 10 000 exp
# Best configurations (first number is the configuration ID; listed from best to worst according to the sum of ranks):
#      t0 t1     a0     a1     a2     r0     r1     r2
# 1202  2  3 0.5880 1.0071 1.9244 0.9648 0.5362 0.4469
# 1244  2  3 0.6735 0.8933 1.9275 0.9806 0.5915 0.3263
# 1326  2  3 0.6819 0.8919 1.9383 0.9717 0.5862 0.3223
# 1329  2  3 0.7165 0.8942 1.9480 0.9660 0.6087 0.3163
# 1185  2  3 0.5769 0.9709 1.8972 0.9792 0.5963 0.3160


#best configs for 50 robots, 400x400, 3000 steps, 10 000 exp
#      t0 t1     a0     a1     a2     r0     r1     r2
# 1146  3  7 0.5919 1.4127 1.9413 0.9611 0.6677 0.0226
# 1170  3  5 0.5482 0.8800 1.9641 0.9767 0.4179 0.5335
# 1000  4  6 0.5508 1.8605 1.9094 0.9246 0.6126 0.1083
# 1147  4  6 0.5140 1.8304 1.9348 0.8867 0.5776 0.0974
# 1010  3  7 0.6370 1.5181 1.9852 0.9187 0.6515 0.0594


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
