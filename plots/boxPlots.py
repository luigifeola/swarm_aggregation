import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

boxplot_df = pd.DataFrame()
for k in range(10):
    input("Please enter something: ")
    results_size = 30
    results = []
    for i in range(results_size):
        df = pd.read_csv("../results/log" + str(i) + ".csv")
        results.append(df["cluster_metric"].iloc[-1])

    boxplot_df['config_' + str(k)] = results

    # print("Median: %f 25th quartile: %f 75th quartile: %f", df_medians["cluster_metric"].iloc[-1], df_quantile25["cluster_metric"].iloc[-1], df_quantile75["cluster_metric"].iloc[-1])

print(boxplot_df.head())
boxplot_df.to_csv('configs_behavior_1.csv')
boxplot = boxplot_df.boxplot(column = ['config_0', 'config_1', 'config_2', 'config_3', 'config_4', 'config_5', 'config_6', 'config_7', 'config_8', 'config_9'])
boxplot.set_ylim(0,1)
boxplot.plot()
plt.show()
