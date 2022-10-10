# Leverage networkx package 
import numpy as np
import networkx as nx
import pandas as pd

G = nx.read_gexf('data/networkx.xml')
stations = pd.read_csv('data/10stations_map.csv')

n = len(stations)
# tau = np.zeros((n, n))
# for i in range(1, n):
#     for j in range(i):
#         i_node = stations.iloc[i]['nearest_node']
#         j_node = stations.iloc[j]['nearest_node']
#         tau[i, j] = nx.astar_path_length(G, str(int(i_node)), str(int(j_node)), weight='timer')
#         tau[j, i] = tau[i, j]
# df = pd.DataFrame(tau)
# df.to_csv('data/tau_matrix_10.csv', index=False)
df = pd.read_csv('data/tau_matrix_10.csv')
tau = df.to_numpy()
large_station = [2, 4, 9]
for i in large_station:
    tau[i, :] = tau[i, :] + 240
    tau[:, i] = tau[:, i] + 240 
tau[2, 4] -= 240
tau[4, 2] -= 240
tau[2, 9] -= 240
tau[9, 2] -= 240
tau[4, 9] -= 240
tau[9, 4] -= 240
tau = np.ceil(tau / 480)
np.fill_diagonal(tau, 0)
tau.astype(int)

def get_station_node(station_id: int):
    return stations.iloc[station_id]['nearest_node']

def get_time(begin: float, final: float):
    orig = str(int(begin))
    dest = str(int(final))
    duration = nx.astar_path_length(G, orig, dest, weight='timer')
    return duration

def get_path_and_distance(begin, final):
    orig = str(int(begin))
    dest = str(int(final))
    path = nx.astar_path(G, orig, dest, weight='timer')
    distance = nx.path_weight(G, path, weight = 'length')
    return path, distance

def get_trip_time_matrix(): 
    return tau

def station_from_far_to_close():
    res = []
    for i in range(n):
        arr = tau[i]
        sort_index = np.argsort(arr)
        reversed_sort = list(sort_index)[::-1]
        res.append(reversed_sort)

    return res
