from math import ceil
import numpy as np
import pandas as pd
import datetime
import time
from vehicle import Veh
from request import Req
from utility import *
from map import get_station_node, get_time, get_path_and_distance, station_from_far_to_close

class Simulator(object):
    """
    Model is the initial class for the SAMoD system
    Attributes:
        vehs: the list of vehicles
        reqs: the list of all received requests
        T: system time
    """

    def __init__(self, fleet_size: int, num_stations: int, soc: int, horizon: int, request_path):
        self.T = 0
        self.n = num_stations
        self.n_v = fleet_size
        self.soc = soc
        self.horizon = horizon
        # Initialize the fleet.
        self.vehs = []
        self.vehs_status = [[fleet_size], [0], [0], [0], [0], [0]]
        for i in range(fleet_size):
            station_idx = int(i * num_stations / fleet_size)
            node_id = get_station_node(station_idx)
            self.vehs.append(Veh(i, station_idx, node_id, soc))
        # Requests in one day, from 00:00:00 to 24:00:00
        self.request = pd.read_csv(request_path)
        self.req_full_list = []
        self.staions_far_to_close = station_from_far_to_close()

    def step(self):
        self.T += 1
        for veh in self.vehs:
            veh.move()
            # every 4 mins


    # Update newly avaliable vehicles for matching algo.
    # Return list of vaccant/occupied Veh at each station
    def update_vehs(self, last, now, period, flag):
        vaccant_vehs = [[[] for _ in range(self.soc)] for i in range(self.n)]
        occupied_vehs = [[[] for _ in range(self.soc)] for i in range(self.n)]
        for veh in self.vehs:
            # if veh status is charging and battery < 80 %, does not move it and lets it continue charging
            if veh.status == VehicleStatus.CHARGING and veh.battery >= 80:
                veh.idling()
                vaccant_vehs[veh.pos][int(veh.battery * self.soc / 100)].append(veh)
                continue
            if veh.status == VehicleStatus.IDLE and last <= veh.arrival_time < now:
                if veh.battery < 20:
                    veh.charging(self.T)
                else:
                    vaccant_vehs[veh.pos][int(veh.battery * self.soc / 100)].append(veh)
                continue
            if veh.status == VehicleStatus.WAITING and last <= veh.arrival_time < now:
                occupied_vehs[veh.pos][int(veh.battery * self.soc / 100)].append(veh)
                continue
            
        return vaccant_vehs, occupied_vehs


    # Update newly poping-up requests for matching algo.
    # Return list of Req at each station
    def update_reqs(self, time, pre_pointer):
        new_req = [[] for _ in range(self.n)]
        if pre_pointer == len(self.request):
            return new_req, pre_pointer
        for i in range(pre_pointer, len(self.request)):
            timestamp = self.request.iloc[i]['Pickup time']
            t = self.time_convert(timestamp)
            if t >= time:
                pointer = i
                break
            orig = self.request.iloc[i]['Source node id']
            dest = self.request.iloc[i]['Dest node id']
            orig_station = self.request.iloc[i]['orig_station']
            dest_station = self.request.iloc[i]['dest_station']
            req = Req(i, t, orig_station, dest_station, orig, dest)
            new_req[orig_station].append(req)
            self.req_full_list.append(req)
        
        # End
        if i == len(self.request) - 1:
            pointer = len(self.request)

        return new_req, pointer


    # Read number of requests inside horizon for controller
    # Return number of requests from one staion to another, a np array
    def read_reqs(self, time, interval, pre_pointer = 0):
        flag = True
        time_slots = [self.T + interval * (i+1) for i in range(self.horizon + 1)]
        # request(i,j,t) sent to controller
        req = np.zeros((self.n, self.n, self.horizon + 1))
        if pre_pointer == len(self.request):
            return req, pre_pointer
        for i in range(pre_pointer, len(self.request)):
            timestamp = self.request.iloc[i]['Pickup time']
            t = self.time_convert(timestamp)
            if t >= time + interval * (self.horizon+1):
                break
            if t >= time + interval and flag:
                pointer = i
                flag = False
            orig_station = self.request.iloc[i]['orig_station']
            dest_station = self.request.iloc[i]['dest_station']
            for idx, time_slot in enumerate(time_slots):
                if t < time_slot:
                    req[orig_station, dest_station, idx] += 1
                    break
            
            #  End
            if i == len(self.request) - 1 and t < time + interval:
                pointer = len(self.request)
            
        return req, pointer
    

    # Read number of vehs inside horizon for controller
    # Return number of vaccant/charging/occupied vehicles at each staion, np array
    def read_vehs(self, interval):
        num_charging_vehs = np.zeros((self.n, self.horizon + 1, self.soc))
        num_vaccant_vehs = np.zeros((self.n, self.horizon + 1, self.soc))
        num_occupied_vehs = np.zeros((self.n, self.horizon + 1, self.soc, self.n))
        for veh in self.vehs:
            if veh.status == VehicleStatus.CHARGING:
                t = int(ceil((80 - veh.battery) / veh.charge) / interval)
                if t > self.horizon:
                    continue
                # num_charging_vehs[veh.pos, t, int(veh.battery * self.soc / 100)] += 1
                num_charging_vehs[veh.pos, t, 8] += 1
                continue
            if veh.status == VehicleStatus.IDLE:
                if veh.battery < 20:
                    continue
                else:
                    num_vaccant_vehs[veh.pos, 0, int(veh.battery * self.soc / 100)] += 1
                    continue
            if veh.status == VehicleStatus.REBALANCING:
                t = int((veh.arrival_time - self.T) / interval)
                if t > self.horizon:
                    continue
                if veh.arrival_soc < 0:
                    num_vaccant_vehs[veh.route[-1], t, 0] += 1
                else:
                    num_vaccant_vehs[veh.route[-1], t, veh.arrival_soc] += 1
                continue
            if veh.status == VehicleStatus.WORKING:
                t = int((veh.arrival_time - self.T) / interval)
                if t > self.horizon:
                    continue
                if veh.route[-1] == veh.route[-2]:
                    if veh.arrival_soc < 0:
                        num_vaccant_vehs[veh.route[-1], t, 0] += 1
                    else:
                        num_vaccant_vehs[veh.route[-1], t, veh.arrival_soc] += 1
                if veh.route[-1] != veh.route[-2]:
                    if veh.arrival_soc < 0:
                        num_occupied_vehs[veh.route[-1], t, 0] += 1
                    else:
                        num_occupied_vehs[veh.route[-2], t, veh.arrival_soc, veh.route[-1]] += 1
                continue
            if veh.status == VehicleStatus.WAITING:
                num_occupied_vehs[veh.pos, 0, int(veh.battery * self.soc / 100), veh.route[-1]] += 1
        
        return num_vaccant_vehs, num_charging_vehs, num_occupied_vehs


    # Extracting info from the optimizater's result
    def read_control_sequence(self, x_zo: np.array, x_so: np.array, p_so: np.array, p_zo: np.array, 
                                r: np.array, c: np.array):
        charging = np.copy(c)
        rebalancing = np.copy(r)
        idling = np.zeros((self.n, self.soc))
        x_one_customer = [[[] for b in range(self.soc)] for i in range(self.n)]
        x_no_customer = [[[] for b in range(self.soc)] for i in range(self.n)]
        p_two_customers = [[[] for b in range(self.soc)] for i in range(self.n)]
        p_one_customer = [[[] for b in range(self.soc)] for i in range(self.n)]
        for i in range(self.n):
            for b in range(self.soc):
                for j in range(self.n):
                    if i == j:
                        rebalancing[i, j, b] = 0
                        if r[i, j, b] != 0:
                            # num of idling vehicles
                            idling[i, b] = r[i, j, b]
                    for m in range(self.n):
                        while x_zo[i, j, m, b] > 0:
                            x_one_customer[i][b].append((j, m))
                            x_zo[i, j, m, b] -= 1
                        while x_so[i, j, m, b] > 0:
                            x_no_customer[i][b].append((j, m))
                            x_so[i, j, m, b] -= 1
                        while p_zo[i, j, m, b] > 0:
                            p_two_customers[i][b].append((j, m))
                            p_zo[i, j, m, b] -=1
                        while p_so[i, j, m, b] > 0:
                            p_one_customer[i][b].append((j, m))
                            p_so[i, j, m, b] -=1

        return idling, rebalancing, charging, x_one_customer, x_no_customer, p_one_customer, p_two_customers


    # Matching algorithm which runs at higher frequency to match newly available vehicles and pop-up results
    def matching(self, popup_reqs: list[list[Req]], idle, r, c, x_zo, x_so, p_so, p_zo, new_vac_vehs: list[list[list[Veh]]], new_occ_vehs: list[list[list[Veh]]]):
        veh_req_pair = {}
        del_set = set()
        requests = popup_reqs.copy()
        vaccant_vehs = new_vac_vehs.copy()
        occupied_vehs = new_occ_vehs.copy()
        for i in range(self.n):
            pending_reqs = requests[i]
            in_station_reqs = []
            for req in pending_reqs:
                print('request:', req.id)
                if req.onid == req.dnid:
                    in_station_reqs.append(req)
            for b in range(self.soc):
                vac_vehs = vaccant_vehs[i][b]
                occ_vehs = occupied_vehs[i][b]
                
                # Executing the control sequence

                # Matching the single occupied vehicles
                # Firstly, the vehicles can pick up one more customer. p_so
                if occ_vehs and p_so[i][b]:
                    num_veh = len(occ_vehs)
                    for idx, veh in enumerate(occ_vehs):
                        for req in pending_reqs:
                            if req.dnid == veh.route[-1] and (req.dnid, req.dnid) in p_so[i][b]:
                                dest = (req.dnid, req.dnid)
                                veh_req_pair.update({'Veh'+str(veh.id):'Req'+str(req.id)})
                                veh.update_onboard(req)
                                self.routing(veh, 'picking up', (), veh.loc, req.orig)
                                self.routing(veh, 'dropping off', dest, req.orig, veh.onboard_req[0].dest, req.dest)
                                del_set.add(idx)
                                num_veh -= 1
                                pending_reqs.remove(req)
                                p_so[i][b].remove(dest)
                                break
                        if num_veh == 0 or not p_so[i][b]: break
                    occ_vehs = [e for i, e in enumerate(occ_vehs) if i not in del_set]
                    del_set.clear()

                # Secondly, the vehicles do not have to pick up customers. x_so
                if occ_vehs and x_so[i][b]:
                    num_veh = len(occ_vehs)
                    for idx, veh in enumerate(occ_vehs):
                        for dest in x_so[i][b]:
                            if veh.route[-1] == dest[1]:
                                if dest[0] == dest[1]:
                                    self.routing(veh, 'dropping off', dest, veh.loc, veh.onboard_req[0].dest)
                                else:
                                    self.routing(veh, 'driving', dest, veh.loc, get_station_node(dest[0]))
                                del_set.add(idx)
                                num_veh -= 1
                                x_so[i][b].remove(dest)
                                break
                        if num_veh == 0 or not x_so[i][b]: break
                    occ_vehs = [e for i, e in enumerate(occ_vehs) if i not in del_set]
                    del_set.clear()
                
                occupied_vehs[i][b] = occ_vehs

                # Match the vaccant vehicles, including vhicles at charging state
                # Firstly, Satisfy the charging sequence at the beginning, left c_vehs and vac_vehs for service. To guarantee the soc
                if c[i, b] >= len(vac_vehs):
                    for veh in vac_vehs:
                        veh.charging(self.T)
                    c[i, b] -= len(vac_vehs)
                    vac_vehs.clear()
                
                if c[i, b] < len(vac_vehs):
                    while c[i, b] > 0 and vac_vehs:
                        veh = vac_vehs.pop()
                        veh.charging(self.T)
                        c[i, b] -= 1
                
                # Secondly, check if 2 requests can be picked up together
                if vac_vehs and p_zo[i][b]:
                    num = len(p_zo[i][b])
                    for idx, dest in enumerate(p_zo[i][b]):
                        count1 = 0
                        count2 = 0
                        for req in pending_reqs:
                            if req.dnid == dest[0]:
                                count1 += 1
                                if count1 == 1:
                                    req1 = req
                                if count1 == 2 and dest[0] == dest[1]:
                                    req2 = req
                                    count2 = 1
                            elif req.dnid == dest[1]:
                                count2 += 1
                                if count2 == 1:
                                    req2 = req                          
                            if count1 >= 1 and count2 >= 1:
                                veh = self.find_nearest_veh(req1.orig, vac_vehs)
                                veh_req_pair.update({'Veh'+str(veh.id):'Req'+str(req1.id) + ', Req'+str(req2.id)})
                                veh.update_onboard(req1, req2)
                                self.routing(veh, 'picking up', (), veh.loc, req1.orig, req2.orig)
                                if dest[0] == dest[1]:
                                    self.routing(veh, 'dropping off', dest, req2.orig, req1.dest, req2.dest)
                                else:
                                    self.routing(veh, 'dropping off', dest, req2.orig, req1.dest)
                                vac_vehs.remove(veh)
                                pending_reqs.remove(req1)
                                pending_reqs.remove(req2)
                                del_set.add(idx)
                                num -= 1
                                break
                        if num == 0 or not vac_vehs: break
                    p_zo[i][b] = [e for i, e in enumerate(p_zo[i][b]) if i not in del_set]
                    del_set.clear()
                
                # Thirdly, match the vehicles which pick up only one customer to reqeusts
                if vac_vehs and x_zo[i][b]:
                    num = len(x_zo[i][b])
                    for idx, dest in enumerate(x_zo[i][b]):
                        for req in pending_reqs:
                            if req.dnid == dest[1]:
                                veh = self.find_nearest_veh(req.orig, vac_vehs)
                                vac_vehs.remove(veh)
                                pending_reqs.remove(req)
                                veh_req_pair.update({'Veh'+str(veh.id):'Req'+str(req.id)})
                                veh.update_onboard(req)
                                self.routing(veh, 'picking up', (), veh.loc, req.orig)
                                if dest[0] == dest[1]:
                                    self.routing(veh, 'dropping off', dest, req.orig, req.dest)
                                else:
                                    self.routing(veh, 'driving', dest, req.orig, get_station_node(dest[0]))
                                del_set.add(idx)
                                num -= 1
                                break
                        if num == 0 or not vac_vehs: break
                    x_zo[i][b] = [e for i, e in enumerate(x_zo[i][b]) if i not in del_set]
                    del_set.clear()
                
                # Rarely, pick up the customer travelling inside one station
                if b > 1 and vac_vehs and in_station_reqs:
                    for idx, req in enumerate(in_station_reqs):
                        veh = self.find_nearest_veh(req.orig, vac_vehs)
                        veh_req_pair.update({'Veh'+str(veh.id):'Req'+str(req.id)})
                        veh.update_onboard(req)
                        self.routing(veh, 'picking up', (), veh.loc, req.orig)
                        self.routing(veh, 'dropping off', (req.onid, req.onid), req.orig, req.dest)
                        vac_vehs.remove(veh)
                        pending_reqs.remove(req)
                        del_set.add(idx)
                        if not vac_vehs: break
                    in_station_reqs = [e for i, e in enumerate(in_station_reqs) if i not in del_set]
                    del_set.clear()
                        
                # Finally, the rest of vaccant vehicles are sent to rebalance and idle. r & idle
                for j in self.staions_far_to_close[i]:
                    while r[i, j, b] > 0 and vac_vehs:
                        veh = vac_vehs.pop()
                        self.routing(veh, 'rebalancing', [j], veh.loc, get_station_node(j))
                        r[i, j, b] -= 1
                
                # No action to idling vehicles, they remain the idle state
                if vac_vehs:
                    for veh in vac_vehs:
                        veh.idling()

        return veh_req_pair, requests, vaccant_vehs, occupied_vehs, idle, r, c, x_zo, x_so, p_so, p_zo
    

    def routing(self, veh: Veh, type: str, dest: tuple, orig_id: float, dest_id1: float, dest_id2=None):
        travel_time = get_time(orig_id, dest_id1)
        path, distance = get_path_and_distance(orig_id, dest_id1)
        if type == 'picking up' and dest_id2 is None:
            veh.pickup_one(travel_time, distance)
            return
        if type == 'picking up' and dest_id2 is not None:
            travel_time2 = get_time(dest_id1, dest_id2)
            path2, distance2 = get_path_and_distance(dest_id1, dest_id2)
            veh.pickup_two(travel_time, travel_time2, distance + distance2)
            return
        if type == 'dropping off' and dest_id2 is None:
            dest = list(dest)
            veh.dropoff_one(dest, path, travel_time, distance)
            return
        if type == 'dropping off' and dest_id2 is not None:
            dest = list(dest)
            travel_time2 = get_time(dest_id1, dest_id2)
            path2, distance2 = get_path_and_distance(dest_id1, dest_id2)
            veh.dropoff_two(dest, path, path2, travel_time, travel_time2, distance + distance2)
            return
        if type == 'driving' and dest_id2 is None:
            dest = list(dest)
            veh.driving(dest, path, travel_time, distance)
            return
        if type == 'rebalancing' and dest_id2 is None:
            dest = list(dest)
            veh.rebalancing(dest, path, travel_time, distance)
            return


    def time_convert(self, timestamp: str):
        x = time.strptime(timestamp,'%H:%M:%S')
        t = datetime.timedelta(hours=x.tm_hour,minutes=x.tm_min,seconds=x.tm_sec).total_seconds()
        return t


    # Return type: Veh
    def find_nearest_veh(self, req_loc: float, available_vehs: list[Veh]):
        min = np.inf
        for veh in available_vehs:
            dist = get_time(req_loc, veh.loc)
            if dist < min:
                dist = min
                nearest_veh = veh
        return nearest_veh
    

    def update_veh_status(self):
        if self.T % 120 == 0:
            n_idle = -20  # at station 2
            n_work = 0
            n_charge = 0
            n_rebalance = 0
            total_energy = 0
            charged_energy = 0
            for veh in self.vehs:
                total_energy += veh.battery * 20 / 100
                charged_energy += veh.energy_charged
                if veh.status == VehicleStatus.IDLE:
                    n_idle += 1
                if veh.status == VehicleStatus.WORKING:
                    n_work += 1
                if veh.status == VehicleStatus.REBALANCING:
                    n_rebalance += 1
                if veh.status == VehicleStatus.CHARGING:
                    n_charge += 1
            self.vehs_status[0].append(n_idle)
            self.vehs_status[1].append(n_work)
            self.vehs_status[2].append(n_rebalance)
            self.vehs_status[3].append(n_charge)
            self.vehs_status[4].append(total_energy)
            self.vehs_status[5].append(charged_energy)


    def get_result(self):
        T = [2 * i for i in range(781)]        
        veh_status = {'Time': T, 'number of idle vehicles': self.vehs_status[0], 'number of serving vehicles': self.vehs_status[1],
                    'number of rebalance vehicles': self.vehs_status[2], 'number of charge vehicles': self.vehs_status[3]}
        system_energy = {'Time': T, 'total energy in vehicles': self.vehs_status[4]}
        charged_energy = {'Time': T, 'total energy in vehicles': self.vehs_status[5]}

        req_id = []
        req_submit_T = []
        req_pickup_T = []
        req_dropoff_T = []
        for req in self.req_full_list:
            req_id.append(req.id)
            req_submit_T.append(req.Tr)
            req_pickup_T.append(req.Tp)
            req_dropoff_T.append(req.Td)
        req_result = {'Request Id': req_id, 'Submission time': req_submit_T, 'Pickup time': req_pickup_T, 'Dropoff time': req_dropoff_T}

        veh_id = []
        veh_battery = []
        veh_energy = []
        veh_pickup_d = []
        veh_rebalance_d = []
        veh_customer_d = []
        for veh in self.vehs:
            veh_id.append(veh.id)
            veh_battery.append(veh.battery)
            veh_energy.append(veh.energy_charged)
            veh_pickup_d.append(veh.D_pick)
            veh_rebalance_d.append(veh.Dr)
            veh_customer_d.append(veh.Ds)
        veh_result = {'Vehicle Id': veh_id, 'Battery': veh_battery, 'Pickup distance': veh_pickup_d, 'With customer distance': veh_customer_d,
                    'Rebalancing distance': veh_rebalance_d, 'Charged energy': veh_energy}
        
        df1 = pd.DataFrame(req_result)
        df2 = pd.DataFrame(veh_result)
        df3 = pd.DataFrame(veh_status)
        df4 = pd.DataFrame(system_energy)
        df5 = pd.DataFrame(charged_energy)
        df1.to_csv('result/request status 200 vehicle 2.csv', index=False)
        df2.to_csv('result/vehicle status 200 vehicle 2.csv', index=False)
        df3.to_csv('result/number of vehicle status 200 vehicle 2.csv', index=False)
        df4.to_csv('result/system energy 200 vehicle 2.csv', index=False)
        df5.to_csv('result/charged energy 200 vehicle 2.csv', index=False)