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
        list_ijktb = []
        list_ijtb = []
        list_itb = []
        list_ijt = []
        list_ib = []
        for i in range(self.n):
            for j in range(self.n):
                for t in range(self.horizon + 1):
                    if i != j:
                        odt = i,j,t
                        list_ijt.append(odt)
                    for b in range(self.soc):
                        odtb = i,j,t,b
                        list_ijtb.append(odtb)
                        for k in range(self.n):
                            oddtb = i,j,k,t,b
                            list_ijktb.append(oddtb)
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
        ijktb = gp.tuplelist(list_ijktb)
        ib = gp.tuplelist(list_ib)

        mpc = gp.Model(name = 'RAMoD_EV MILP')

        # objective function
        obj = 0
        # Control variables
        c = mpc.addVars(itb, vtype = GRB.INTEGER, name = 'c')
        r = mpc.addVars(ijtb, vtype = GRB.INTEGER, name = 'r')
        x_zo = mpc.addVars(ijktb, vtype = GRB.INTEGER, name = 'x_zo')
        x_so = mpc.addVars(ijktb, vtype = GRB.INTEGER, name = 'x_so')
        p_zo = mpc.addVars(ijktb, vtype = GRB.INTEGER, name = 'p_zo')
        p_so = mpc.addVars(ijktb, vtype = GRB.INTEGER, name = 'p_so')
        x = mpc.addVars(ijktb, vtype = GRB.INTEGER, name = 'x')
        p = mpc.addVars(ijktb, vtype = GRB.INTEGER, name = 'p')
        d = mpc.addVars(ijt, vtype = GRB.INTEGER, lb = 0, name = 'd')

        # Constraints: x = x_zo + x_so, p = p_zo + p_so
        mpc.addConstrs((x[i, j, k, t, b] == x_so[i, j, k, t, b] + x_zo[i, j, k, t, b] for i,j,k,t,b in ijktb), name = 'Total x_veh num')
        mpc.addConstrs((p[i, j, k, t, b] == p_so[i, j, k, t, b] + p_zo[i, j, k, t, b] for i,j,k,t,b in ijktb), name = 'Total p_veh num')
        # Constraints: disallowed movement
        mpc.addConstrs((x[i, i, k, t, b] == 0 for i,j,k,t,b in ijktb), name = 'disallowed')
        mpc.addConstrs((p[i, i, k, t, b] == 0 for i,j,k,t,b in ijktb), name = 'disallowed')
        mpc.addConstrs((x_zo[i, j, i, t, b] == 0 for i,j,k,t,b in ijktb), name = 'disallowed')
        mpc.addConstrs((p_so[i, j, i, t, b] == 0 for i,j,k,t,b in ijktb), name = 'disallowed')

        for t in range(0, self.horizon + 1):
            for i in range(self.n):
                if t >= self.tau_max[i]:
                    available_j_0 = [j for j in range(self.n) if j != i]
                else:
                    available_j_0 = np.where((t - self.tau[i, :]) >= 0)[0].tolist()
                    available_j_0.remove(i)
                for b in range(self.soc):
                    available_j = [j for j in available_j_0 if (b + self.delta_b[i, j]) < self.soc]
                    reachable_j = [j for j in range(self.n) if (b - self.delta_b[i, j]) > 0 and j != i]
                    
                    left_sum0 = 0
                    right_sum0 = 0
                    unreachable_j = [j for j in range(self.n) if j not in reachable_j and j != i]
                    mpc.addConstrs((r[i, j, t, b] == 0 for j in unreachable_j), name = 'disallowed')   
                    for j in reachable_j:
                        right_sum0 += r[i, j, t, b]
                        if b - self.delta_b[i, j] == 1:
                            right_sum0 += x_zo[i, j, j, t, b] + p_zo[i, j, j, t, b]
                            k_range = [k for k in range(self.n) if k != j]
                            mpc.addConstrs((x_zo[i, j, k, t, b] == 0 for k in k_range), name = 'disallowed')
                            mpc.addConstrs((p_zo[i, j, k, t, b] == 0 for k in k_range), name = 'disallowed')
                        else:
                            for k in range(self.n):
                                if (b - self.delta_b[i, j] - self.delta_b[j, k]) > 1 and k != i:
                                    right_sum0 += x_zo[i, j, k, t, b] + p_zo[i, j, k, t, b]
                                if (b - self.delta_b[i, j] - self.delta_b[j, k]) <= 1 and k != i:
                                    mpc.addConstr(x_zo[i, j, k, t, b] == 0, name = 'disallowed')
                                    mpc.addConstr(p_zo[i, j, k, t, b] == 0, name = 'disallowed')

                    if t == 0:
                        if b >= 8:
                            mpc.addConstr(veh_idle[i, 0, b] + veh_charging[i, 0, b] == right_sum0 + r[i, i, 0, b], name = 'Initial vaccant veh conservation')
                        elif b >= 2:
                            mpc.addConstr(veh_idle[i, 0, b] == right_sum0 + r[i, i, 0, b], name = 'Initial vaccant veh conservation')
                        else:
                            mpc.addConstr(veh_idle[i, 0, b] == c[i, 0, b], name = 'Initial vaccant veh conservation')

                    # Constraints during the horizon
                    else:
                        for j in available_j:
                            left_sum0 += r[j, i, t-self.tau[i, j], b+self.delta_b[i, j]] + x[j, i, i, t-self.tau[i, j], b+self.delta_b[i, j]] + p[j, i, i, t-self.tau[i, j], b+self.delta_b[i, j]]
                        if b >= 8:
                            # mpc.addConstr(veh_idle[i, t, b] + veh_charging[i, t, b] + r[i, i, t-1, b] + left_sum0 == r[i, i, t, b] + right_sum0,
                            #     name = 'vaccant veh conservation')
                            if b == 9 and t >= 2:
                                mpc.addConstr(veh_idle[i, t, b] + veh_charging[i, t, b] + r[i, i, t-1, b] + left_sum0 + c[i, t-2, 1] == r[i, i, t, b] + right_sum0,
                                    name = 'vaccant veh conservation')
                            if b == 9 and t == 1:
                                mpc.addConstr(veh_idle[i, t, b] + veh_charging[i, t, b] + r[i, i, t-1, b] + left_sum0 == r[i, i, t, b] + right_sum0,
                                    name = 'vaccant veh conservation')
                            if b == 8 and t >= 2:
                                mpc.addConstr(veh_idle[i, t, b] + veh_charging[i, t, b] + r[i, i, t-1, b] + left_sum0 + c[i, t-2, 0] == r[i, i, t, b] + right_sum0,
                                    name = 'vaccant veh conservation')
                            if b == 8 and t == 1:
                                mpc.addConstr(veh_idle[i, t, b] + veh_charging[i, t, b] + r[i, i, t-1, b] + left_sum0 == r[i, i, t, b] + right_sum0,
                                    name = 'vaccant veh conservation')
                        elif b >= 2:
                            mpc.addConstr(veh_idle[i, t, b] + r[i, i, t-1, b] + left_sum0 == r[i, i, t, b] + right_sum0,
                                name = 'vaccant veh conservation')
                        else:
                            mpc.addConstr(veh_idle[i, t, b] == c[i, t, b], name = 'vaccant veh conservation')
                    
                    # For single occupied vehicles
                    for m in range(self.n):
                        right_sum1 = 0
                        left_sum1 = 0
                        # Pickup another customer only when its destination is the same as the onboard customer's
                        if m in reachable_j:
                            right_sum1 = p_so[i, m, m, t, b]
                            for j in range(self.n):
                                if j != m:
                                    mpc.addConstr(p_so[i, j, m, t, b] == 0, name = 'disallowed')
                                if (b - self.delta_b[i, j] - self.delta_b[j, m]) > 0:
                                    right_sum1 += x_so[i, j, m, t, b]
                                if (b - self.delta_b[i, j] - self.delta_b[j, m]) <= 0:
                                    if j == m:
                                        right_sum1 += x_so[i, j, m, t, b]
                                    else:
                                        mpc.addConstr(x_so[i, j, m, t, b] == 0, name = 'disallowed')
                            # Initial Constraints
                            if t == 0:
                                mpc.addConstr((veh_occupied[i, 0, b, m] == right_sum1), name = 'Initial x_veh')
                            # Constraints during the horizon
                            else:
                                for o in available_j:
                                    left_sum1 += x[o, i, m, t-self.tau[i, o], b+self.delta_b[i, o]] + p[o, i, m, t-self.tau[i, o], b+self.delta_b[i, o]]
                                mpc.addConstr((left_sum1 + veh_occupied[i, t, b, m] == right_sum1), name = 'single occupied veh conservation')
                        else:
                            mpc.addConstrs((x[i, m, _, t, b] == 0 for _ in range(self.n)), name = 'Low_soc_veh x cannot move')
                            mpc.addConstrs((x[i, _, m, t, b] == 0 for _ in range(self.n)), name = 'Low_soc_veh x cannot move')
                            mpc.addConstrs((p[i, _, m, t, b] == 0 for _ in range(self.n)), name = 'Low_soc_veh p cannot move')
                            mpc.addConstrs((p[i, m, _, t, b] == 0 for _ in range(self.n)), name = 'Low_soc_veh p cannot move')


                for j in range(self.n):
                    if j != i and t == 0:
                        mpc.addConstr(d[i, j, 0] == requests[i, j, 0] - p_so.sum(i, j, j, 0, '*') - gp.quicksum(x_zo[i, k, j, 0, b] 
                        + p_zo[i, k, j, 0, b] + p_zo[i, j, k, 0, b] for k,b in ib), name = 'Remain requests t=0')
                        obj -= self.Vd*d[i,j,0] + self.tau[i, j] * (self.Vr*r.sum(i,j,0,'*') + gp.quicksum(self.Vx*x[i,j,k,0,b] + self.Vp*p[i,j,k,0,b] for k,b in ib))
                    if j != i and t > 0:
                        mpc.addConstr(d[i, j, t] == requests[i, j, t] + d[i, j ,t-1] - p_so.sum(i, j, j, t, '*') - gp.quicksum(x_zo[i, k, j, t, b]
                        + p_zo[i, k, j, t, b] + p_zo[i, j, k, t, b] for k,b in ib), name = 'Remain requests')
                        obj -= self.Vd*d[i, j, t] + self.tau[i, j] * (self.Vr*r.sum(i,j,t,'*') + gp.quicksum(self.Vx*x[i,j,k,t,b] + self.Vp*p[i,j,k,t,b] for k,b in ib))

        mpc.setObjective(obj, GRB.MAXIMIZE)
        mpc.Params.MIPFocus = 3
        mpc.Params.MIPGap = 0.01
        # Verify model formulation and save as MPS file
        mpc.write('RAMoD_EV MILP.lp')
        # Run optimization engine
        mpc.optimize()

        # Output control policy
        x_zo_0 = np.zeros((self.n, self.n, self.n, self.soc))
        x_so_0 = np.zeros((self.n, self.n, self.n, self.soc))
        p_zo_0 = np.zeros((self.n, self.n, self.n, self.soc))
        p_so_0 = np.zeros((self.n, self.n, self.n, self.soc))
        r_0 = np.zeros((self.n, self.n, self.soc))
        c_0 = np.zeros((self.n, self.soc))

        for i in range(self.n):
            for b in range(self.soc):
                for j in range(self.n):
                    r_0[i, j, b] = r[i, j, 0, b].x
                    for k in range(self.n):
                        x_zo_0[i, j, k, b] = x_zo[i, j, k, 0, b].x
                        x_so_0[i, j, k, b] = x_so[i, j, k, 0, b].x
                        p_zo_0[i, j, k, b] = p_zo[i, j, k, 0, b].x
                        p_so_0[i, j, k, b] = p_so[i, j, k, 0, b].x

        print('c_0 = ', np.where(c_0 != 0))
        print('r_0 = ', np.where(r_0 != 0))
        print('x_so_0 = ', np.where(x_so_0 != 0))
        print('x_zo_0 = ', np.where(x_zo_0 != 0))
        print('p_zo_0 = ', np.where(p_zo_0 != 0))
        print('p_so_0 = ', np.where(p_so_0 != 0))

        return x_zo_0, x_so_0,p_zo_0, p_so_0, r_0, c_0