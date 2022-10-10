from urllib import request
import numpy as np
from collections import deque
import pandas as pd
from pyparsing import delimited_list

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
# df1 = df.iloc[1103:1662, :]
# df1.to_csv('data/requests_10_stations_test.csv', index=False)

# df = pd.read_csv('data/tau_matrix_10.csv')
# tau = df.to_numpy()
# tau = np.ceil(tau / 360)
# tau.astype(int)
# print(tau)

# tau2 = df.to_numpy()
# large_station = [2, 4, 9]
# for i in large_station:
#     tau2[i, :] = tau2[i, :] + 180
#     tau2[:, i] = tau2[:, i] + 180 
# tau2[2, 4] -= 180
# tau2[4, 2] -= 180
# tau2[2, 9] -= 180
# tau2[9, 2] -= 180
# tau2[4, 9] -= 180
# tau2[9, 4] -= 180
# tau2 = np.ceil(tau2 / 360)
# np.fill_diagonal(tau2, 0)
# tau2.astype(int)
# print(tau2)

# df1 = pd.read_csv('result/number of vehicle status.csv')
# df1.iloc[:, 1] -= 10
# df1.to_csv('result/number of vehicle status.csv', index=False)

df1 = pd.read_csv('Heuristic charge 20kWh final/result/system energy 200 vehicle.csv')
df1.iloc[0, 1] = 4000.00
df1.to_csv('Heuristic charge 20kWh final/result/system energy 200 vehicle.csv', index=False)