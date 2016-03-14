from enum import Enum


class IpReason(Enum):
    Success = 0,
    Timeout = 1,
    Cancelled = 2
    
    
class IpResult(object):
    def __init__(self, ip_address, reason):
        self.ip_address = ip_address
        self.reason = reason
