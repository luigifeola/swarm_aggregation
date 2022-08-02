import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import igraph as ig
from math import dist

def get_neighbors_graph(neighbors_table):
    edges = []
    for i in range(len(neighbors_table)):
        for j in range(len(neighbors_table[i])):
            edges.append((i,int(neighbors_table[i][j][6])))

    graph = ig.Graph(edges= edges)
    return graph

results_size = 10
results = []
neighbors_table = [[] for i in range(results_size)]


for i in range(1, results_size + 1):
    metrics_data = [[] for f in range(3)]
    df = pd.read_csv("Results/robot_positions_" + str(i) + ".csv")

    #compute neighbors table

    pop_size = (int(df.shape[1]) - 1)/2
    pop_size = int(pop_size)

    # plot lines
    # for line in range(pop_size):
    #     plt.plot(df["robot_" + str(line) + "_x"].iloc[2800:3000], df["robot_" + str(line) + "_y"].iloc[2800:3000], label = str(line))
    # plt.show()

    for j in range(df.shape[0]):
        neighbors_table = [[] for k in range(pop_size)]
        for id1 in range(pop_size):
            for id2 in range(id1 + 1, pop_size):
                a = (df["robot_" + str(id1) + "_x"].iloc[j], df["robot_" + str(id1) + "_y"].iloc[j])
                b = (df["robot_" + str(id2) + "_x"].iloc[j], df["robot_" + str(id2) + "_y"].iloc[j])
                if dist(a, b) <= 0.1:
                    neighbors_table[id1].append("robot_" + str(id2))
                    neighbors_table[id2].append("robot_" + str(id1))
        #3. Compute metrics
        total_distance = 0
        for id1 in range(pop_size):
            for id2 in range(pop_size):
                if id1 != id2:
                    a = (df["robot_" + str(id1) + "_x"].iloc[j], df["robot_" + str(id1) + "_y"].iloc[j])
                    b = (df["robot_" + str(id2) + "_x"].iloc[j], df["robot_" + str(id2) + "_y"].iloc[j])
                    total_distance += dist(a, b)
        total_distance = -total_distance

        clusters = get_neighbors_graph(neighbors_table).clusters()
        # print("Number of clusters = %d" % len(clusters))
        max = 0
        cluster_count = len(clusters)
        for cluster in clusters:
            if(len(cluster) > max):
                max = len(cluster)
            if(len(cluster)==1):
                cluster_count -= 1

        # print("Largest cluster size = %d" % max)
        cluster_metric = max/pop_size
        # print("Cluster metric = %f" % cluster_metric)

        metrics_data[0].append(cluster_count)
        metrics_data[1].append(cluster_metric)
        metrics_data[2].append(total_distance)
        # print(j)

    # print(metrics_data)
    df_metrics = pd.DataFrame(data = metrics_data)
    df_metrics = df_metrics.transpose()
    df_metrics.columns= ['cluster_count', 'cluster_metric', 'total_distance']
    print(df_metrics)
    results.append(df_metrics)


df_concat = pd.concat(results)
by_row_index = df_concat.groupby(df_concat.index)
df_medians = by_row_index.median()
df_quantile25 = by_row_index.quantile(q = 0.25)
df_quantile75 = by_row_index.quantile(q = 0.75)
print(df_medians.head())
print(df_quantile25.head())
print(df_quantile75.head())

ax = plt.gca()
df_medians.plot(kind='line', y='cluster_count', color = 'blue', ax=ax, ylim=(0,50))
df_quantile25.plot(kind='line', y='cluster_count', color = 'blue', ax=ax, legend=False, ylim=(0,50))
df_quantile75.plot(kind='line', y='cluster_count', color = 'blue', ax=ax, legend=False, ylim=(0,50))
plt.fill_between(df_medians.index, df_quantile25.cluster_count, df_quantile75.cluster_count)
plt.show()

ax = plt.gca()
df_medians.plot(kind='line', y='cluster_metric', color = 'blue', ax=ax, ylim=(0,1))
df_quantile25.plot(kind='line', y='cluster_metric', color = 'blue', ax=ax, ylim=(0,1), legend=False)
df_quantile75.plot(kind='line', y='cluster_metric', color = 'blue', ax=ax, ylim=(0,1), legend=False)
plt.fill_between(df_medians.index, df_quantile25.cluster_metric, df_quantile75.cluster_metric)
plt.show()

ax = plt.gca()
df_medians.plot(kind='line', y='total_distance', color = 'blue', ax=ax)
df_quantile25.plot(kind='line', y='total_distance', color = 'blue', ax=ax, legend=False)
df_quantile75.plot(kind='line', y='total_distance', color = 'blue', ax=ax, legend=False)
plt.fill_between(df_medians.index, df_quantile25.total_distance, df_quantile75.total_distance)
plt.show()
