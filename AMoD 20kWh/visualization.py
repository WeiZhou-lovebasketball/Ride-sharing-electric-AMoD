import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import math
import time
import datetime


# reqs = pd.read_csv('data/requests_10_stations_test.csv')
# t = [2 * i for i in range(61)]
# t = np.array(t)
# reqs_t = np.zeros(61)
# # accumulate_reqs = np.zeros(31)
# for i in range(0, len(reqs)):
#     timestamp = reqs.iloc[i]['Pickup time']
#     x = time.strptime(timestamp,'%H:%M:%S')
#     second = datetime.timedelta(hours=x.tm_hour,minutes=x.tm_min,seconds=x.tm_sec).total_seconds()
#     idx = math.ceil((second - 3600 * 8) / 120)
#     reqs_t[idx] += 1
# for i in range(1, len(reqs_t)):
#     accumulate_reqs[i] = reqs_t[i] + accumulate_reqs[i-1]

# plt.plot(t, reqs_t, 'b', label = 'popup request')
# plt.plot(t, accumulate_reqs, 'r', label = 'accumulated request')
# plt.title('Reqeust from 8:00 am to 9:00 am')
# plt.legend(loc = "upper left")
# plt.xlabel('time / mins')
# plt.ylabel('number of request')

# ax = plt.gca()
# df2 = pd.read_csv('result/waiting customers.csv')
# df2.plot(kind = 'line', x = 'Time', y = 'number of waiting customers', color = 'black', ax = ax)
# plt.show()
# plt.savefig('result/reqeust status')
# popup_reqs = {'Time': t, 'popup requests': reqs_t}
# req_data = pd.DataFrame(popup_reqs)

df1 = pd.read_csv('result/waiting customers normal.csv')
df1.rename(columns={'number of waiting customers': 'AMoD'}, inplace=True)
df2 = pd.read_csv('result/waiting customers RAMoD.csv')
df2.rename(columns={'number of waiting customers': 'RAMoD'}, inplace = True)
df3 = pd.read_csv('result/waiting customers 200 vehicle.csv')
df3.rename(columns={'number of waiting customers': 'AMoD: num of vehicles = 200'}, inplace = True)
dfa = df1.merge(df2, on='Time')
dfb = dfa.merge(df3, on='Time')
dfb['Time'] = [round((8.00 + 2 * i / 60), 2) for i in range(61)]
dfb.to_csv('result/waiting customers comparison.csv', index=False)
df = pd.read_csv('result/waiting customers comparison.csv', index_col=0, parse_dates=True)
ax = df.plot()
plt.title('Waiting reqeusts from 8:00 am to 10:00 am')
plt.xlabel('time [hour]')
plt.ylabel('number of requests')
ax.set_xticks([8, 8.25, 8.5, 8.75, 9, 9.25, 9.5, 9.75, 10], ['8:00', '8:15', '8:30', '8:45', '9:00', '9:15', '9:30', '9:45', '10:00'])
plt.savefig('result/waiting customers 2')

# df1 = pd.read_csv('result/system energy 200 vehicle RAMoD.csv')
# df1.rename(columns={'total energy in vehicles': 'RAMoD: num of vehicles = 200'}, inplace=True)
# df2 = pd.read_csv('result/system energy 300 vehicle RAMoD.csv')
# df2.rename(columns={'total energy in vehicles': 'RAMoD: num of vehicles = 300'}, inplace=True)
# df3 = pd.read_csv('result/system energy 200 vehicle AMoD.csv')
# df3.loc[0, 'total energy in vehicles'] = 4000.00
# df3.rename(columns={'total energy in vehicles': 'AMoD: num of vehicles = 200'}, inplace=True)
# df4 = pd.read_csv('result/system energy 300 vehicle AMoD.csv')
# df4.loc[0, 'total energy in vehicles'] = 6000.00
# df4.rename(columns={'total energy in vehicles': 'AMoD: num of vehicles = 300'}, inplace=True)
# dfa = df1.merge(df2, on='Time')
# dfb = dfa.merge(df3, on='Time')
# df = dfb.merge(df4, on='Time')
# df['Time'] = [round((0.00 + 2 * i / 60), 2) for i in range(751)]
# df.to_csv('result/4 group of system energy comparison.csv', index=False)
# df = pd.read_csv('result/4 group of system energy comparison.csv', index_col=0, parse_dates=True)
# df.plot()
# plt.title('System energy from 00:00 am to 25:00 am')
# plt.xlabel('time [hour]')
# plt.ylabel('Total energy [kWh]')
# # plt.legend(loc = 'lower left')
# plt.savefig('result/4 group of system energy comparison')