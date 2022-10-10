from multiprocessing.connection import wait
from matplotlib.pyplot import nipy_spectral
from MPC import Controller
from Platform import Simulator
import numpy as np
import pandas as pd

if __name__ == '__main__':
    n = 10     # number of stations
    n_v = 200   # number of vehicles
    horizon = 4   # prediction horizon, time = t*T
    interval = 480    # time interval = 8 min
    matching_interval = 30   # frequency of executing the matching algo. once in 30s
    soc = 10   # 20 kWh battery, per soc represents 2 kWh
    # soc = 20   # 40 kWh battery, per soc represents 2 kWh
    T = 0     # system clock, 's'
    request_path = 'data/requests_10_stations_in_order_new.csv'
    waiting_customers = [0]
    # Initialize the SAMoD model with all vaccant vehicles evenly distributed
    simulator = Simulator(n_v, n, soc, horizon, request_path)
    # Initialize the MPC controller
    MPC = Controller(n, soc, horizon)
    # Initial vehicle states, evenly distributed
    init_vehs = np.zeros((n, horizon+1, soc))
    init_vehs[:, 0, soc-1] = int(n_v / n)
    # Initial requets
    init_reqs, controller_pointer = simulator.read_reqs(T, interval)
    # Initial variables
    matching_pointer = 0
    boolean = True
    left_reqs, left_vac_vehs, left_occ_vehs = [], [], []
    # Computer actions for T = 0
    x_zo, x_so, p_zo, p_so, r, c = MPC.compute_actions(init_vehs, np.zeros((n, soc)), np.zeros((n, horizon+1, soc, n)), init_reqs)
    # i, r, c: np.array, x_zo, x_so, p_so, p_zo: list of destination (j, m)
    idle, rebalance, charge, x_pickone, x_nopick, p_pickone, p_picktwo = simulator.read_control_sequence(x_zo, x_so, p_so, p_zo, r, c)

    while T < 3600 * 26:
        T += 1
        simulator.step()
        # Run matching algorithm at higher frequency
        if T % matching_interval == 0:
            popup_reqs, matching_pointer = simulator.update_reqs(T, matching_pointer)
            new_vac_vehs, new_occ_vehs = simulator.update_vehs(T - matching_interval, T, interval, boolean)
            boolean = False
            if left_reqs:
                for i in range(n):
                    popup_reqs[i] = left_reqs[i] + popup_reqs[i]
            if left_vac_vehs:
                for i in range(n):
                    for b in range(soc):
                        new_vac_vehs[i][b] = left_vac_vehs[i][b] + new_vac_vehs[i][b]
            if left_occ_vehs:
                for i in range(n):
                    for b in range(soc):
                        new_occ_vehs[i][b] = left_occ_vehs[i][b] + new_occ_vehs[i][b]

            # Run the matching algo.
            veh_req_pair, left_reqs, left_vac_vehs, left_occ_vehs, idle, rebalance, charge, x_pickone, x_nopick, p_pickone, p_picktwo = simulator.matching(popup_reqs,
             idle, rebalance, charge, x_pickone, x_nopick, p_pickone, p_picktwo, new_vac_vehs, new_occ_vehs)

            print('Matching vehicle and request:', veh_req_pair)

            simulator.update_veh_status()

            # every 2 mins
            if T % 120 == 0:
                waiting_customer = 0
                for i in range(n):
                    waiting_customer += len(left_reqs[i])
                waiting_customers.append(waiting_customer)

        # Compute actions at the start of every interval
        if T % interval == 0:
            # Update the variable for a new round of control sequences and matching
            boolean = True

            # Observe the idling and occupied vehicles with SOC b at station i, type: np.array
            n_s, n_c, n_sx = simulator.read_vehs(interval)
            # Collect the requests to be dealt with
            considering_reqs, controller_pointer = simulator.read_reqs(T, interval, controller_pointer)
            for i in range(n):
                for left_req in left_reqs[i]:
                    considering_reqs[i, left_req.dnid, 0] += 1
            # Compute the control sequence in a receding horizon way
            x_zo, x_so, p_zo, p_so, r, c = MPC.compute_actions(n_s, n_c, n_sx, considering_reqs)
            idle, rebalance, charge, x_pickone, x_nopick, p_pickone, p_picktwo = simulator.read_control_sequence(x_zo, x_so, p_so, p_zo, r, c)


    simulator.get_result()
    time = [2 * i for i in range(781)]
    waiting_c = {'Time': time, 'number of waiting customers': waiting_customers}
    df = pd.DataFrame(waiting_c)
    df.to_csv('result/waiting customers 200 vehicle copy.csv', index=False)