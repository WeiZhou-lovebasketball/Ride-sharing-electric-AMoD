"""
definition of requests for the AMoD system
"""

from utility import OrderStatus


class Req(object):
    """
    Req is a class for requests
    Attributes:
        id: sequential unique id
        Tr: request time
        onid: origin station
        dnid: destination station
        orig: origin location
        dest: destination location
        Tp: actually pickup time
        Td: actually dropoff time
    """

    def __init__(self, id: int, Tr: int, onid: int, dnid: int, orig: float, dest: float):
        self.id = id
        self.status = OrderStatus.PENDING
        self.Tr = Tr
        self.onid = onid
        self.dnid = dnid
        self.orig = orig
        self.dest = dest
        self.Tp = -1.0
        self.Td = -1.0
        # self.waiting_T = 0.0

    def pickup(self, t: int):
        self.Tp = t
        assert self.status == OrderStatus.PENDING 
        self.status = OrderStatus.ONBOARD
        # self.waiting_T = t - self.Tr

    def dropoff(self, t: int):
        self.Td = t
        assert self.status == OrderStatus.ONBOARD
        self.status = OrderStatus.COMPLETE
