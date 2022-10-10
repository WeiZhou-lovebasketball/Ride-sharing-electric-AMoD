import numpy as np
from collections import deque
import pandas as pd
import time
import datetime
import math

# l1 = [[i] for i in range(2)]
# print(l1)
# l2 = [[[i] for i in range(11, 13)] for t in range(5)]
# print(l2)
# l1[0] = l1[0] + l2[1][0]
# l1[1] = l1[1] + l2[1][1]
# print(l1)
# list = [[[1]for _ in range(2)] for i in range(2)]
# print(list[1][1])
array = np.ones((3, 2))
pos = 10
print('array', array[0,0])
o = 1
# with open('record.txt', 'w') as f:
#     f.write('vehicle pos: {}, with {} customer onboard. \n'.format(pos, o))
#     f.write('End')

b = [[4, 5], [5, 6]]
a = [[1, 2, 3],[]]
print(a+b)

# tau = np.ones((2, 4))
# tau[0,0] = 2
# list = np.where((1-tau[0,:]) >= 0)[0].tolist()
# print(list)

# vehs = [1, 2, 3, 4, 5]
# def test(list):
#     a = list
#     a.remove(1)
#     return list

# print(vehs)
# test(vehs)
# print(vehs)
 
path = deque([1, 2])
path.clear()
path.extend([3, 4, 5])
print(path[-1])

dict = {}
car_number = 1
request_number = 2
dict.update({'Veh'+ str(car_number): 'Req' + str(request_number) + ', Req'+str(3)})
print(dict)
# for item in dict:
#     print(dict[item])

# unwanted = set()
# test = [(0, 1), (2, 3), (3, 4)]
# for idx, num in enumerate(test):
#     if 3 in num:
#         unwanted.add(idx)
# test = [e for i, e in enumerate(test) if i not in unwanted]
# print(test)

# x = 5
# y = 0
# z = 100
# def test1(x, y):
#     x += 1
#     y += 1
#     return x, y, x+y
# T = 0
# while T < 5:
#     x, y, z = test1(x, y)
#     T += 1


# v = 5
# if test and 3 < v < 10:
#     print('hello')

# a = np.zeros((2, 2))
# if not a.all():
#     print('hello!')
# a[1, 1] = 1
# a[0, 0] = 2
# print(np.transpose(np.nonzero(a)))
# print(a[np.nonzero(a)])
# print(np.shape(a)[0])


# arr = [1, 2, 3]
# for i in range(10):
#     for k in arr:
#         print(arr)
#         arr.remove(k)
#         break

abc = []
if not abc:
    print('yes')
# df = pd.read_csv('data/requests_10_stations_in_order_new.csv')
# type(df.iloc[0]['Pickup time'])
# del_list = []
# for i in range(0, len(df)):
#     if df.iloc[i]['orig_station'] == 2 or df.iloc[i]['dest_station'] == 2:
#         del_list.append(i)
# df.drop(del_list, inplace=True)
# df.to_csv('data/requests_10_stations_in_order_new.csv', index=False)

# df = pd.read_csv('data/tau_matrix_10.csv')
# tau = df.to_numpy()
# tau = np.ceil(tau / 480)
# tau.astype(int)
# print(tau)

# tau2 = df.to_numpy()
# large_station = [2, 4, 9]
# for i in large_station:
#     tau2[i, :] = tau2[i, :] + 240
#     tau2[:, i] = tau2[:, i] + 240 
# tau2[2, 4] -= 240
# tau2[4, 2] -= 240
# tau2[2, 9] -= 240
# tau2[9, 2] -= 240
# tau2[4, 9] -= 240

# tau2[9, 4] -= 240
# tau2 = np.ceil(tau2 / 480)
# np.fill_diagonal(tau2, 0)
# tau2.astype(int)
# print(tau2)

# list21 = [[1,2], [], [3, 4]]
# print(len(list21[1]))

# popup requests
# reqs = pd.read_csv('data/requests_10_stations_in_order_new.csv')
# t = [2 * i for i in range(751)]
# t = np.array(t)
# reqs_t = np.zeros(751)
# for i in range(0, len(reqs)):
#     timestamp = reqs.iloc[i]['Pickup time']
#     x = time.strptime(timestamp,'%H:%M:%S')
#     second = datetime.timedelta(hours=x.tm_hour,minutes=x.tm_min,seconds=x.tm_sec).total_seconds()
#     idx = math.ceil(second / 120)
#     reqs_t[idx] += 1
# popup_reqs = {'Time': t, 'popup requests': reqs_t}
# req_data = pd.DataFrame(popup_reqs)
# req_data.to_csv('data/popup requests.csv', index=False)

df1 = pd.read_csv('RAMoD 20kWh final/result/system energy 200 vehicle.csv')
df1.iloc[0, 1] = 4000.00
df1.to_csv('RAMoD 20kWh final/result/system energy 200 vehicle.csv', index=False)