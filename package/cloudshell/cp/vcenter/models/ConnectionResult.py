class ConnectionResult(object):
    def __init__(self, mac_address, vnic_name, requested_vnic, vm_uuid, network_name, network_key):
        self.mac_address = mac_address
        self.requested_vnic = requested_vnic
        self.vm_uuid = vm_uuid
        self.network_name = network_name
        self.network_key = network_key
        self.vnic_name = vnic_name
