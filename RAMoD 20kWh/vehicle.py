"""
definition of the vehicles for RAMoD system
"""

import math
from copyreg import pickle
from tracemalloc import start
from collections import deque
from turtle import distance
from utility import VehicleStatus

class Veh(object):
    """
    Veh is a class of vehicles
    Attributes:
        id: sequential unique id
        status: idle, working, charging and rebalancing
        pos: current station position, -1 means on road and unavailable
        loc: node id
        o: zero, single, double occupancy
        T: synchronized system clock
        battery: the state of charge of the battery
        soc: state of charge, ranging from 0 to 9, which represents an interval of 10%
        decharge/charge: vehicle decharge and charge rate
        n_soc: number of soc sections
        route: a list of stations
        arrival_time = system clock when arriving at a station
        arrival_soc = vehicle soc when arriving at a station
        Ds: accumulated service distance traveled
        Ts: accumulated service time traveled
        Dr: accumulated rebalancing distance traveled
        Tr: accumulated rebalancing time traveled
        Cs: accumulated customer served
        path_record: list of the nodes, actual path travelled
    """

    def __init__(self, id: int, station: int, location: float, n_soc: int):
        self.id = id
        self.status = VehicleStatus.IDLE
        self.pos = station
        self.loc = location
        self.o = 0
        self.T = 0
        self.battery = 99.99   # 100 %, 20 kWh
        self.decharge = 5 / 360  # 6 min for 1 kWh, 5 %
        self.charge = 5 / 60    # fast charging 60 kW, 16 min for 80 % (16 kWh), 1 min 5 %
        self.n_soc = n_soc
        self.route = deque([station])
        self.arrival_time = 0
        self.arrival_soc = 0
        self.Ds = 0.0
        self.Ts = 0
        self.D_pick = 0.0
        self.T_pick = 0
        self.Dr = 0.0
        self.Tr = 0
        self.path_record = deque([])
        self.pickup_time = []
        self.onboard_req = []   # list of Req
        self.charging_start_t = 0
        self.energy_charged = 0
        self.battery_after_pick = 0
    
    def move(self):
        self.T += 1
        if self.status == VehicleStatus.IDLE:
            return
        if self.status == VehicleStatus.CHARGING:
            if self.battery == 99.99:
                return
            self.battery += self.charge
            self.energy_charged += self.charge * 20 / 100
            if self.battery > 99.99:
                self.battery = 99.99
                return
        if self.status == VehicleStatus.WORKING or self.status == VehicleStatus.REBALANCING:
            if self.T != math.ceil(self.arrival_time):
                self.pos = -1
                self.battery -= self.decharge
                return
            else:
                self.route.popleft()
                self.pos = self.route[0]
                self.loc = self.path_record[-1]
                if self.status == VehicleStatus.WORKING:
                    # Single occupancy taxi whoes route end and the customer destination are the same,
                    # is going to drop off the onboard customer. Otherwise, it keeps the status as working
                    # and the route would be (current pos, customer destination)
                    if self.o == 1:
                        if self.route[0] == self.route[1]:
                            self.route.pop()
                            self.o = 0
                            self.status = VehicleStatus.IDLE
                            self.onboard_req.clear()
                        else:
                            self.status = VehicleStatus.WAITING
                    # double occupancy taxi where two customers destinations are the same, is going to drop
                    # off both. Otherwise, it keeps the status as working, drop off the first customer
                    # and the route would be (current pos, onboard customer destination)
                    if self.o == 2:
                        if self.route[0] == self.route[1]:
                            self.route.pop()
                            self.o = 0
                            self.status = VehicleStatus.IDLE
                            self.onboard_req.clear()
                        else:
                            self.o = 1
                            del self.onboard_req[0]
                            self.status = VehicleStatus.WAITING

                if self.status == VehicleStatus.REBALANCING:
                    self.status = VehicleStatus.IDLE

                self.path_record.clear()
        
        # assert self.battery >= -50, 'Battery Runs Out Error!'

        return

    def idling(self):
        self.status = VehicleStatus.IDLE

    def charging(self, start_time):
        self.status = VehicleStatus.CHARGING
        self.charging_start_t = start_time
        self.arrival_time = -1

    def rebalancing(self, dest, path, time, distance):
        self.status = VehicleStatus.REBALANCING
        self.route.extend(dest)
        self.path_record.extend(path)
        self.Tr += time
        self.Dr += distance
        self.arrival_time = self.T + time
        self.arrival_soc = int((self.battery - time * self.decharge) * self.n_soc / 100)

    def update_onboard(self, req1, req2=None):
        assert self.o <= 2
        self.onboard_req.append(req1)
        self.o += 1
        if req2:
            self.onboard_req.append(req2)
            self.o += 1

    def pickup_one(self, time, distance):
        pickup_time = self.T + time
        self.onboard_req[-1].pickup(self.T)
        self.battery_after_pick = self.battery - time * self.decharge
        self.pickup_time.append(pickup_time)
        self.T_pick += time
        self.D_pick += distance

    def pickup_two(self, time1, time2, distance):
        pickup_time1 = self.T + time1
        pickup_time2 = self.T + time1 + time2
        self.onboard_req[0].pickup(self.T)
        self.onboard_req[1].pickup(self.T)
        self.battery_after_pick = self.battery - (time1 + time2) * self.decharge
        self.pickup_time.append(pickup_time1)
        self.pickup_time.append(pickup_time2)
        self.T_pick += (time1 + time2)
        self.D_pick += distance
    
    def driving(self, dest, path, time, distance):
        # Happends in x_so and x_zo that are not going to drop off any customer
        self.status = VehicleStatus.WORKING
        # x_zo
        if len(self.route) == 1:
            self.arrival_time = self.pickup_time[-1] + time
            self.arrival_soc = int((self.battery_after_pick - time * self.decharge) * self.n_soc / 100)
        # x_so
        if len(self.route) == 2:
            self.route.pop()
            self.arrival_time = self.T + time
            self.arrival_soc = int((self.battery - time * self.decharge) * self.n_soc / 100)
        self.route.extend(dest)
        self.path_record.extend(path)
        self.Ts = time
        self.Ds += distance


    def dropoff_one(self, dest, path, time, distance):
        # Happends in x_so, p_zo, x_zo
        self.status = VehicleStatus.WORKING
        # p_zo have pick up time
        if self.o == 2:
            self.arrival_time = self.pickup_time[-1] + time
            self.arrival_soc = int((self.battery_after_pick - time * self.decharge) * self.n_soc / 100)
        # x_zo
        if self.o == 1 and len(self.route) == 1:
            self.arrival_time = self.pickup_time[-1] + time
            self.arrival_soc = int((self.battery_after_pick - time * self.decharge) * self.n_soc / 100)
        # x_so
        if len(self.route) == 2:
            self.arrival_time = self.T + time
            self.route.pop()
            self.arrival_soc = int((self.battery - time * self.decharge) * self.n_soc / 100)
        self.route.extend(dest)
        self.path_record.extend(path)
        self.Ts = time
        self.Ds += distance
        # vehicle driving inside-station customer
        if self.o == 1 and self.route[0] == self.route[1]:
            self.arrival_time = self.pickup_time[0] + time
            self.arrival_soc = int((self.battery_after_pick - time * self.decharge) * self.n_soc / 100)
            self.onboard_req[0].dropoff(self.arrival_time)
            self.pickup_time.clear()
            return
        self.onboard_req[0].dropoff(self.arrival_time)
        self.pickup_time.clear()
        return  
    
    def dropoff_two(self, dest, path1, path2, time1, time2, distance):
        # Happends in p_zo, p_so
        self.status = VehicleStatus.WORKING
        if len(self.route) == 2:
            self.route.pop()
        self.route.extend(dest)
        path = path1 + path2
        self.path_record.extend(path)
        time = time1 + time2
        self.Ts += time
        self.Ds += distance
        self.arrival_time = self.pickup_time[-1] + time1
        self.onboard_req[0].dropoff(self.arrival_time)
        self.arrival_time += time2
        self.onboard_req[1].dropoff(self.arrival_time)
        self.pickup_time.clear()
        self.arrival_soc = int((self.battery_after_pick - time * self.decharge) * self.n_soc / 100)