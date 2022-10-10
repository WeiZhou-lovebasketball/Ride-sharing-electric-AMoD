import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# # Mean waiting time
# df = pd.read_csv('result/request status.csv')
# wait_t = np.zeros(len(df))
# journey_t = np.zeros(len(df))
# for i in range(len(df)):
#     sub_t = df.iloc[i]['Submission time']
#     pick_t = df.iloc[i]['Pickup time']
#     drop_t = df.iloc[i]['Dropoff time']
#     wait_t[i] = pick_t - sub_t
#     journey_t[i] = drop_t - pick_t

# print('Mean waiting time =', np.mean(wait_t))
# print('Mean journey time =', np.mean(journey_t))

# waiting customers plot
# df1 = pd.read_csv('result/waiting customers 200 vehicle.csv')
# df1.rename(columns={'number of waiting customers': 'RAMoD: num of vehicles = 200'}, inplace=True)
# df2 = pd.read_csv('result/waiting customers 300 vehicle.csv')
# df2.rename(columns={'number of waiting customers': 'RAMoD: num of vehicles = 300'}, inplace=True)
# df3 = pd.read_csv('result/waiting customers 200 vehicle AMoD.csv')
# df3.rename(columns={'number of waiting customers': 'AMoD: num of vehicles = 200'}, inplace=True)
# df4 = pd.read_csv('result/waiting customers 300 vehicle AMoD.csv')
# df4.rename(columns={'number of waiting customers': 'AMoD: num of vehicles = 300'}, inplace=True)
# df = df1.merge(df2, on='Time')
# dfa = df.merge(df3, on='Time')
# dfb = dfa.merge(df4, on='Time')
# dfb['Time'] = [round((0.00 + 2 * i / 60), 2) for i in range(751)]
# dfb.to_csv('result/4 group of waiting customers comparison.csv', index=False)
df = pd.read_csv('result/waiting customers 200 vehicle.csv', index_col=0, parse_dates=True)
df.plot()
plt.title('Waiting requests from 00:00 am to 26:00 am')
plt.xlabel('time [min]')
plt.ylabel('number of requests')
plt.savefig('result/waiting customers')

# energy plot
# df1 = pd.read_csv('result/system energy 200 vehicle.csv')
# df1.rename(columns={'total energy in vehicles': 'RAMoD: num of vehicles = 200'}, inplace=True)
# df2 = pd.read_csv('result/system energy 300 vehicle.csv')
# df2.rename(columns={'total energy in vehicles': 'RAMoD: num of vehicles = 300'}, inplace=True)
# df = df1.merge(df2, on='Time')
# df['Time'] = [round((0.00 + 2 * i / 60), 2) for i in range(751)]
# df.to_csv('result/system energy comparison.csv', index=False)
# df = pd.read_csv('result/system energy comparison.csv', index_col=0, parse_dates=True)
# df.plot()
# plt.title('System energy from 00:00 am to 25:00 am')
# plt.xlabel('time [hour]')
# plt.ylabel('Total energy [kWh]')
# plt.savefig('result/system energy comparison')