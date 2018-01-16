import re
from pyVmomi import vim

from cloudshell.cp.vcenter.vm.ip_manager import VMIPManager


class VmDetailsProvider(object):
    def __init__(self, ip_manager):
        self.ip_manager = ip_manager  # type: VMIPManager

    def create(self, vm, resource_model, logger):
        vm_details = VmDetails()
        vm_details.vm_instance_data = self._get_vm_instance_data(vm)
        vm_details.vm_network_data = self._get_vm_network_data(vm, resource_model, logger)
        return vm_details

    def _get_vm_instance_data(self, vm):
        memo_size_kb = vm.summary.config.memorySizeMB * 1024
        disk_size_kb = next((device.capacityInKB for device in vm.config.hardware.device if
                             isinstance(device, vim.vm.device.VirtualDisk)), 0)
        data = {
            'cpu': vm.summary.config.numCpu,
            'memory': self._convert_kb_to_str(memo_size_kb),
            'disk_size': self._convert_kb_to_str(disk_size_kb),
            'guest_os': vm.summary.config.guestFullName
        }
        return data

    def _get_vm_network_data(self, vm, resource_model, logger):
        data_list = []
        primary_ip = self._try_primary_ip(vm, resource_model, logger)
        for net in vm.guest.net:
            vlan_name = net.network
            vlan_id = self._try_get_vlan_id(vm, vlan_name)
            ip = next(iter(net.ipAddress), None)
            if vlan_id:
                data = VmNetworkData()
                data.interface_id = net.macAddress
                data.network_id = vlan_id
                data.network_data['mac_address'] = net.macAddress
                data.network_data['vlan_name'] = vlan_name
                if ip:
                    data.network_data['ip'] = ip
                    data.is_primary = primary_ip == ip
                data_list.append(data)

        return data_list

    def _try_primary_ip(self, vm, resource_model, logger):
        match_function = self.ip_manager.get_ip_match_function(resource_model.get_refresh_ip_regex())
        primary_ip = self.ip_manager.get_ip(vm, None, match_function, None, None, logger).ip_address
        return primary_ip

    @staticmethod
    def _try_get_vlan_id(vm, network_name):
        try:
            network = next((n for n in vm.network if n.name == network_name), None)
            vlan_id = network.config.defaultPortConfig.vlan.vlanId
            return VmDetailsProvider._convert_vlan_id_to_str(vlan_id)
        except AttributeError:
            pass
        return None

    @staticmethod
    def _convert_kb_to_str(kb):
        mb = kb / 1024
        gb = mb / 1024
        if gb > 0:
            return '%0.0f GB' % gb
        elif mb > 0:
            return '%0.0f MB' % mb
        else:
            return '%0.0f KB' % kb

    @staticmethod
    def _convert_vlan_id_to_str(vlan_id):
        if vlan_id:
            if isinstance(vlan_id, list):
                return ','.join([VmDetailsProvider._convert_vlan_id_to_str(v) for v in vlan_id if v])

            if isinstance(vlan_id, vim.NumericRange):
                if vlan_id.start == vlan_id.end:
                    return '%s' % vlan_id.start
                else:
                    return '%s-%s' % (vlan_id.start, vlan_id.end)

            if isinstance(vlan_id, str):
                return vlan_id

            if isinstance(vlan_id, int):
                return str(vlan_id)

        return ''


class VmDetails(object):
    def __init__(self):
        self.vm_instance_data = {}  # type: dict
        self.vm_network_data = []  # type: list[VmNetworkData]


class VmNetworkData(object):
    def __init__(self):
        self.interface_id = {}  # type: str
        self.network_id = {}  # type: str
        self.is_primary = False  # type: bool
        self.network_data = {}  # type: dict
