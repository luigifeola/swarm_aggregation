import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# boxplot_df = pd.DataFrame()
# for k in range(10):
#     input("Please enter something: ")
#     results_size = 30
#     results = []
#     for i in range(results_size):
#         df = pd.read_csv("../results/log" + str(i) + ".csv")
#         results.append(df["cluster_metric"].iloc[-1])
#
#     boxplot_df['config_' + str(k)] = results
#
#     # print("Median: %f 25th quartile: %f 75th quartile: %f", df_medians["cluster_metric"].iloc[-1], df_quantile25["cluster_metric"].iloc[-1], df_quantile75["cluster_metric"].iloc[-1])
#
# print(boxplot_df.head())
# boxplot_df.to_csv('configs_second_behavior_10e5_budget.csv')
# boxplot = boxplot_df.boxplot(column = ['irace-1114', 'irace-8321', 'irace-17830', 'irace-2348161', 'irace-2373604', 'irace-2394777', 'irace-2454947', 'irace-2469279', 'irace-4172462', 'irace-4187919'])
# boxplot.set_ylim(0,1)
# boxplot.plot()
# plt.show()

df = pd.read_csv('configs_second_behavior_10e5_budget.csv')
boxplot = df.boxplot(column = ['irace-1114', 'irace-8321', 'irace-17830', 'irace-2348161', 'irace-2373604', 'irace-2394777', 'irace-2454947', 'irace-2469279', 'irace-4172462', 'irace-4187919'])
boxplot.set_ylim(0,1)
boxplot.plot()
plt.show()
