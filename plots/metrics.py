import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

results_size = 10
results = []
for i in range(results_size):
    df = pd.read_csv("../results/log" + str(i) + ".csv")
    results.append(df)

print(results)

df_concat = pd.concat(results)
by_row_index = df_concat.groupby(df_concat.index)
df_medians = by_row_index.median()
df_quantile25 = by_row_index.quantile(q = 0.25)
df_quantile75 = by_row_index.quantile(q = 0.75)
print(df_medians.head())
print(df_quantile25.head())
print(df_quantile75.head())

ax = plt.gca()
df_medians.plot(kind='line', y='cluster_number', color = 'blue', ax=ax, ylim=(0,50))
df_quantile25.plot(kind='line', y='cluster_number', color = 'blue', ax=ax, legend=False, ylim=(0,50))
df_quantile75.plot(kind='line', y='cluster_number', color = 'blue', ax=ax, legend=False, ylim=(0,50))
plt.fill_between(df_medians.index, df_quantile25.cluster_number, df_quantile75.cluster_number)
plt.show()

ax = plt.gca()
df_medians.plot(kind='line', y='cluster_metric', color = 'blue', ax=ax, ylim=(0,1))
df_quantile25.plot(kind='line', y='cluster_metric', color = 'blue', ax=ax, ylim=(0,1), legend=False)
df_quantile75.plot(kind='line', y='cluster_metric', color = 'blue', ax=ax, ylim=(0,1), legend=False)
plt.fill_between(df_medians.index, df_quantile25.cluster_metric, df_quantile75.cluster_metric)
plt.show()
