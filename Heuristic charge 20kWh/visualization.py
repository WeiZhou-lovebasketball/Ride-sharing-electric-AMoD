import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import math
import time
import datetime


reqs = pd.read_csv('data/requests_10_stations_test.csv')
t = [2 * i for i in range(61)]
t = np.array(t)
reqs_t = np.zeros(61)
# accumulate_reqs = np.zeros(31)
for i in range(0, len(reqs)):
    timestamp = reqs.iloc[i]['Pickup time']
    x = time.strptime(timestamp,'%H:%M:%S')
    second = datetime.timedelta(hours=x.tm_hour,minutes=x.tm_min,seconds=x.tm_sec).total_seconds()
    idx = math.ceil((second - 3600 * 8) / 120)
    reqs_t[idx] += 1
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
popup_reqs = {'Time': t, 'popup requests': reqs_t}
req_data = pd.DataFrame(popup_reqs)

df1 = pd.read_csv('result/waiting customers no energy.csv')
df1.rename(columns={'number of waiting customers': 'no energy'}, inplace=True)
df2 = pd.read_csv('result/waiting customers normal.csv')
df2.rename(columns={'number of waiting customers': 'num of vehicles = 100'}, inplace = True)
df3 = pd.read_csv('result/waiting customers longer horizon.csv')
df3.rename(columns={'number of waiting customers': 'horizon = 56min'}, inplace= True)
df4 = pd.read_csv('result/waiting customers no consumption.csv')
df4.rename(columns={'number of waiting customers': 'no consumption'}, inplace=True)
df5 = pd.read_csv('result/waiting customers 200 vehicle.csv')
df5.rename(columns={'number of waiting customers': 'num of vehicles = 200'}, inplace=True)
df6 = pd.read_csv('result/waiting customers faster charge.csv')
df6.rename(columns={'number of waiting customers': 'faster charge'}, inplace=True)
dfa = df1.merge(df2, on='Time')
dfb = dfa.merge(df3, on='Time')
dfc = dfb.merge(df4, on='Time')
dfd = dfc.merge(df5, on='Time')
dfe = dfd.merge(df6, on='Time')
dff = dfe.merge(req_data, on='Time')
dff['Time'] = [round((8.00 + 2 * i / 60), 2) for i in range(61)]
dff.to_csv('result/waiting customers of 6 config.csv', index=False)
df = pd.read_csv('result/waiting customers of 6 config.csv', index_col=0, parse_dates=True)
ax = df.plot()
plt.title('Waiting reqeusts from 8:00 am to 10:00 am')
plt.xlabel('time [hour]')
plt.ylabel('number of requests')
ax.set_xticks([8, 8.25, 8.5, 8.75, 9, 9.25, 9.5, 9.75, 10], ['8:00', '8:15', '8:30', '8:45', '9:00', '9:15', '9:30', '9:45', '10:00'])
plt.savefig('result/waiting customers of 6 config')