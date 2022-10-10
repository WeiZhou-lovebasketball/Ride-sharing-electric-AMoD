import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Mean waiting time
df = pd.read_csv('result/request status normal.csv')
wait_t = np.zeros(len(df))
journey_t = np.zeros(len(df))
for i in range(len(df)):
    sub_t = df.iloc[i]['Submission time']
    pick_t = df.iloc[i]['Pickup time']
    drop_t = df.iloc[i]['Dropoff time']
    wait_t[i] = pick_t - sub_t
    journey_t[i] = drop_t - pick_t

print('Mean waiting time =', np.mean(wait_t))
print('Mean journey time =', np.mean(journey_t))

# # waiting customers plot
# df1 = pd.read_csv('result/waiting customers.csv')
# df1.rename(columns={'number of waiting customers': 'waiting'}, inplace=True)
# df2 = pd.read_csv('data/popup requests.csv')
# dfa = df1.merge(df2, on='Time')
# dfa.to_csv('result/popup request vs waiting customers.csv', index=False)
# dfb = pd.read_csv('result/popup request vs waiting customers.csv', index_col=0, parse_dates=True)
# dfb.plot()
# dfb.plot()
# plt.title('Requests status from 00:00 am to 25:00 am')
# plt.xlabel('time [mins]')
# plt.ylabel('number of requests')
# plt.savefig('result/waiting customers')