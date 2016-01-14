from unittest import TestCase

from mock import Mock

from vCenterShell.network.dvswitch.name_generator import DvPortGroupNameGenerator
from vCenterShell.vm.dvswitch_connector import ConnectRequest
from vCenterShell.vm.vnic_to_network_mapper import VnicToNetworkMapper
from pyVmomi import vim


class TestVnicToNetworkMapper(TestCase):

    def test_(self):
        vnics = {'net 1': Mock(spec=vim.vm.device.VirtualEthernetCard),
                 'net 2': Mock(spec=vim.vm.device.VirtualEthernetCard)}
        request1 = ConnectRequest('net 2',Mock(spec=vim.Network))
        request2 = ConnectRequest(None,Mock(spec=vim.Network))
        requests = [request1, request2]
        mapper = VnicToNetworkMapper(DvPortGroupNameGenerator())
        mappig = mapper.map_request_to_vnics(requests,vnics, [], Mock(spec=vim.Network))
        self.assertTrue(mappig[request1.vnic_name], request1.network)
        self.assertTrue(mappig['net 1'], request2.network)
