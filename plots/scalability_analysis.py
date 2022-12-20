import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

column_list = ["swarm_size_25_arena_300","swarm_size_25_arena_400","swarm_size_25_arena_500","swarm_size_25_arena_600",
               "swarm_size_50_arena_300","swarm_size_50_arena_400","swarm_size_50_arena_500","swarm_size_50_arena_600",
               "swarm_size_100_arena_300","swarm_size_100_arena_400","swarm_size_100_arena_500","swarm_size_100_arena_600"]

boxplot_df = pd.DataFrame()
for root, dirs, files in os.walk('../results/scalability_analysis'):
    for dir_name in sorted(dirs, reverse=True):
        results_size = 30
        results = []
        for i in range(results_size):
            df = pd.read_csv("../results/scalability_analysis/" + dir_name + '/log' + str(i) + ".csv")
            results.append(df["cluster_metric"].iloc[-1])

        boxplot_df[dir_name] = results

print(boxplot_df.head())
boxplot_df.to_csv('scalability_analysis.csv')
boxplot = boxplot_df.boxplot(column = column_list, fontsize = 8)
boxplot.set_ylim(0,1)
boxplot.plot()
plt.show()

# df = pd.read_csv('configs_second_behavior_10e5_budget.csv')
# boxplot = df.boxplot(column = ['irace-1114', 'irace-8321', 'irace-17830', 'irace-2348161', 'irace-2373604', 'irace-2394777', 'irace-2454947', 'irace-2469279', 'irace-4172462', 'irace-4187919'])
# boxplot.set_ylim(0,1)
# boxplot.plot()
# plt.show()
