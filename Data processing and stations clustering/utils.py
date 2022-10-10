import pandas as pd
import numpy as np
import matsim

def nearest_node(path):
    stations = pd.read_csv(path)
    net = matsim.read_network('data/network.xml.gz')
    nodes = net.nodes
    nearest_nodes = []
    for i in range(len(stations)):
        min = np.inf
        a = np.array((stations.iloc[i]['x'], stations.iloc[i]['y']))
        for index, node in nodes.iterrows():
            b = np.array((node['x'], node['y']))
            dist = np.linalg.norm(a-b)
            if dist < min:
                min = dist
                nearest_node = node['node_id']
        nearest_nodes.append(nearest_node)

    stations['nearest_node'] = nearest_nodes
    stations.to_csv(path, index=False)

# df = pd.read_csv('requests/pop_orig.csv')
# df1 = pd.read_csv('requests/requests.csv')
# df1.rename(columns = {'id':'Source node id'}, inplace=True)
# dest_node = df["Dest node id"]
# df1.insert(5, 'Dest node id', dest_node)
# df1.to_csv('requests/requests.csv', index=False)

def request_sorting(path):
    df = pd.read_csv(path)
    requests = df.sort_values(by = 'Pickup time', ascending=True)
    requests.to_csv(path, index=False)