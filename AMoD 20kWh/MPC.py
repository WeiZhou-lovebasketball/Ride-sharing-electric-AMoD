import numpy as np
import gurobipy as gp
from gurobipy import GRB
from map import get_trip_time_matrix

class Controller(object):
    def __init__(self, num_stations: int, soc: int, horizon):
        self.n = num_stations
        self.horizon = horizon
        self.soc = soc
        # Type: np.array, trip time between every two stations
        self.tau = get_trip_time_matrix()
        self.tau_max = np.amax(self.tau, axis=1)
        # Charging speed relative to tau
        self.tau_c = 4
        # Depleting speed relative to tau, per 8 min consumes 2 kWh
        decharge = 1
        self.delta_b = self.tau * decharge
        # Tuning weights
        self.Vd = 1000
        self.Vr = 5
        self.Vx = 5
        self.Vp = 5
        self.Vc = 1

    def compute_actions(self, veh_idle, veh_charging, veh_occupied, reqs: np.array):
        # Number of requests from i to j in the horizon of the controller
        requests = np.copy(reqs)

        # Build a list of tuple oddtb (origin, destination, destination, time, SOC),
        # a list of tuple odtb (origin, destination, time, SOC) for rebalancing
        # a list of tuple otb (origin, time, SOC) for charging vehicles
        # and a list of tuple odt for request counting
        list_ijtb = []
        list_itb = []
        list_ijt = []
        list_ib = []
        for i in range(self.n):
            for j in range(self.n):
                for t in range(self.horizon + 1):
                    odt = i,j,t
                    list_ijt.append(odt)
                    for b in range(self.soc):
                        odtb = i,j,t,b
                        list_ijtb.append(odtb)
                        
        for i in range(self.n):
            for b in range(self.soc):
                ob = i,b
                list_ib.append(ob)
                for t in range(self.horizon + 1):
                    otb = i,t,b
                    list_itb.append(otb)                                

        itb = gp.tuplelist(list_itb)
        ijt = gp.tuplelist(list_ijt)
        ijtb = gp.tuplelist(list_ijtb)

        mpc = gp.Model(name = 'AMoD_EV MILP')

        # objective function
        obj = 0
        # Control variables
        r = mpc.addVars(ijtb, vtype = GRB.INTEGER, name = 'r')
        c = mpc.addVars(itb, vtype = GRB.INTEGER, name = 'c')
        x_zo = mpc.addVars(ijtb, vtype = GRB.INTEGER, name = 'x_zo')
        d = mpc.addVars(ijt, vtype = GRB.INTEGER, lb = 0, name = 'd')

        mpc.addConstrs((x_zo[i, i, t, b] == 0 for i, t, b in itb), name = 'disallowed') 

        for t in range(0, self.horizon + 1):
            for i in range(self.n):
                if t >= self.tau_max[i]:
                    available_j_0 = [j for j in range(self.n)]
                else:
                    available_j_0 = np.where((t - self.tau[i, :]) >= 0)[0].tolist()
                # for b = 0
                mpc.addConstrs((r[i, j, t, 0] == 0 for j in range(self.n)), name = 'disallowed')
                mpc.addConstrs((x_zo[i, j, t, 0] == 0 for j in range(self.n)), name = 'disallowed')
                if t == 0:
                    mpc.addConstr(veh_idle[i, 0, 0] + veh_charging[i, 0] == r[i, i, 0, 0] + c[i, 0, 0], name = 'Initial vaccant veh conservation')
                if t > 0:
                    mpc.addConstr(veh_idle[i, t, 0] == r[i, i, t, 0]+ c[i, t, 0], name = 'Initial vaccant veh conservation')
                
                for b in range(1, self.soc):
                    available_j = [j for j in available_j_0 if (b + self.delta_b[i, j]) < self.soc]
                    reachable_j = [j for j in range(self.n) if (b - self.delta_b[i, j]) > 0]
                    unreachable_j = [j for j in range(self.n) if j not in reachable_j]

                    mpc.addConstrs((r[i, j, t, b] == 0 for j in unreachable_j), name = 'disallowed')
                    mpc.addConstrs((x_zo[i, j, t, b] == 0 for j in unreachable_j), name = 'disallowed') 

                    left_sum0 = 0
                    right_sum0 = 0
                    for j in reachable_j:
                        right_sum0 += r[i, j, t, b] + x_zo[i, j, t, b]
                    if t == 0:
                        mpc.addConstr(veh_idle[i, 0, b] + veh_charging[i, b] == right_sum0 + c[i, 0, b], name = 'Initial vaccant veh conservation')

                    # Constraints during the horizon
                    else:
                        for j in available_j:
                            left_sum0 += r[j, i, t-self.tau[i, j], b+self.delta_b[i, j]] + x_zo[j, i, t-self.tau[i, j], b+self.delta_b[i, j]]
                        c_sum = 0
                        if b == self.soc - 1:
                            for k in range(b):
                                if k + self.tau_c >= b:
                                    c_sum += c[i, t - 1, k]
                        if self.tau_c <= b < self.soc - 1:
                            c_sum = c[i, t - 1, b - self.tau_c]
                        mpc.addConstr(veh_idle[i, t, b] + c_sum + left_sum0 == c[i, t, b] + right_sum0, name = 'vaccant veh conservation')


                for j in range(self.n):
                    if t == 0:
                        mpc.addConstr(d[i, j, 0] == requests[i, j, 0] - x_zo.sum(i, j, 0, '*'), name = 'Remain requests t=0')
                        obj -= self.Vd * d[i, j, 0] + self.tau[i, j] * (self.Vr * r.sum(i, j, 0, '*') + self.Vx * x_zo.sum(i, j, 0, '*'))
                    else:
                        mpc.addConstr(d[i, j, t] == requests[i, j, t] + d[i, j ,t-1] - x_zo.sum(i, j, t, '*'), name = 'Remain requests')
                        obj -= self.Vd * d[i, j, t] + self.tau[i, j] * (self.Vr * r.sum(i, j, t, '*') + self.Vx * x_zo.sum(i, j, t, '*'))
                obj -= self.Vc * c.sum(i, t, '*')
        
        mpc.setObjective(obj, GRB.MAXIMIZE)
        mpc.Params.MIPFocus = 3
        mpc.Params.MIPGap = 0.01
        # Verify model formulation and save as MPS file
        mpc.write('AMoD_EV MILP.lp')
        # Run optimization engine
        mpc.optimize()

        # Output control policy
        x_zo_0 = np.zeros((self.n, self.n, self.soc))
        x_so_0 = np.zeros((self.n, self.n, self.n, self.soc))
        p_zo_0 = np.zeros((self.n, self.n, self.n, self.soc))
        p_so_0 = np.zeros((self.n, self.n, self.n, self.soc))
        r_0 = np.zeros((self.n, self.n, self.soc))
        c_0 = np.zeros((self.n, self.soc))

        for i in range(self.n):
            for b in range(self.soc):
                c_0[i, b] = c[i, 0, b].x
                for j in range(self.n):
                    r_0[i, j, b] = r[i, j, 0, b].x
                    x_zo_0[i, j, b] = x_zo[i, j, 0, b].x

        print('c_0 = ', np.where(c_0 != 0))
        print('r_0 = ', np.where(r_0 != 0))
        print('x_zo_0 = ', np.where(x_zo_0 != 0))

        return x_zo_0, x_so_0,p_zo_0, p_so_0, r_0, c_0