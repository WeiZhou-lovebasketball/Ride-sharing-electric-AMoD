from enum import Enum

##################################################################################
# Request (order) and Vehicle Status Types
##################################################################################
class OrderStatus(Enum):
    PENDING = 1
    PICKING = 2
    ONBOARD = 3
    COMPLETE = 4


class VehicleStatus(Enum):
    IDLE = 1
    WORKING = 2
    REBALANCING = 3
    CHARGING = 4
    WAITING = 5
