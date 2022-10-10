from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from utils import nearest_node, request_sorting

data = pd.read_csv('requests/pop_orig.csv')
data_len = len(data)
orig_data = data.loc[:, ['x','y']]
dest_data = data.loc[:,['Dest x', 'Dest y']]
dest_data.columns = ['x', 'y']
OD = pd.concat([orig_data, dest_data], ignore_index=True, sort=False)
# print('OD', OD)
# orig = np.array(orig_data)
# dest = np.array(dest_data)
# plt.scatter(orig[:,0], orig[:,1], marker='o', s=0.8, c='black')
# plt.scatter(dest[:,0], dest[:,1], marker='o', s=0.8, c='red')
# plt.show()

# Clustering
n_stations = 10
colors = np.array(['b','r','m','g','c','gray','orange','y', 'darkred', 'greenyellow', 'pink', 'gold'])
model = KMeans(n_clusters=n_stations, random_state=0).fit(OD)
station_label = model.labels_
stations = model.cluster_centers_
station_id = np.zeros(data_len * 2, dtype = int)
for i in range(n_stations):
    cluster=np.where(station_label==i)[0]
    plt.scatter(OD.x[cluster].values, OD.y[cluster].values, marker='o', s=0.2, c=colors[i], label = i)
    station_id[cluster] = i
plt.scatter(stations[:,0], stations[:,1], marker='d', s=10, c='k')
plt.legend(loc = 'lower left', fontsize = 8)
plt.xlabel('coordinate x', fontsize = 16)
plt.ylabel('coordinate y', fontsize = 16)
plt.savefig('10 stations new')
# orig_station = station_id[:data_len]
# dest_station = station_id[data_len:]
# data['orig_station'] = orig_station
# data['dest_station'] = dest_station
# data.to_csv('requests/requests_10_stations.csv', index=False)
# request_sorting('requests/requests_10_stations.csv')

# stations = pd.DataFrame(stations, columns = ['x', 'y'])
# stations.to_csv('10stations_map.csv', index=False)
# nearest_node('10stations_map.csv')


# score=[]
# # k ranges from 2 to 16
# for i in range(2, 17):
#     model = KMeans(n_clusters=i, init='k-means++', random_state=0)
#     model.fit(OD)
#     score.append(model.inertia_)
# x = [i for i in range(2, 17)]
# plt.plot(x, score, 'bx-')
# plt.xlabel('number of clusters')
# plt.ylabel('inertia')
# plt.show()
                 
# plt.plot(range(2,20), score)
# # A dotline shows with which k the score is highest   
# # idxmax()[] + 2, since k starts from 2 here
# plt.axvline(pd.DataFrame(score).idxmax()[0]+2, ls=':')
# plt.show()

