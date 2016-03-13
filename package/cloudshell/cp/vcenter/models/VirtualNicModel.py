class VirtualNicModel:

    def __init__(self, network_label, mac_address, connected, connect_at_power_on):
        self.networkLabel = network_label
        self.macAddress = mac_address
        self.connected = connected
        self.connectAtPowerOn = connect_at_power_on
