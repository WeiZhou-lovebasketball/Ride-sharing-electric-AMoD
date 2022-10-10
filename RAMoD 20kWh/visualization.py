import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import time
import datetime
import math

reqs = pd.read_csv('data/requests_10_stations_in_order_new.csv')
T = 24 * 60   # 24h in mins
t = [i / 30 for i in range(int(T/2 + 1))]
t = np.array(t)
reqs_t = np.zeros_like(t)
for i in range(0, len(reqs)):
    timestamp = reqs.iloc[i]['Pickup time']
    x = time.strptime(timestamp,'%H:%M:%S')
    second = datetime.timedelta(hours=x.tm_hour,minutes=x.tm_min,seconds=x.tm_sec).total_seconds()
    idx = math.ceil(second / 120)
    reqs_t[idx] += 1

plt.plot(t, reqs_t, 'b', linewidth = 0.5, label = 'popup requests')
# plt.title('New reqeusts from 00:00:00 to 25:00:00')
# plt.legend(loc = "upper right")
plt.grid()
plt.xlabel('time [h]', fontsize = 16)
plt.xlim([0, 24])
plt.ylabel('number of requests', fontsize = 16)
# plt.show()
plt.savefig('requests in one day')