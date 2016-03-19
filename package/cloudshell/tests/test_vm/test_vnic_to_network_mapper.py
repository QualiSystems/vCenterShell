from unittest import TestCase

from mock import Mock
from pyVmomi import vim
from cloudshell.cp.vcenter.vm.dvswitch_connector import ConnectRequest
from cloudshell.cp.vcenter.vm.vnic_to_network_mapper import VnicToNetworkMapper

from cloudshell.cp.vcenter.network.dvswitch.name_generator import DvPortGroupNameGenerator


class TestVnicToNetworkMapper(TestCase):

    def test_(self):
        vnics = {'net 1': Mock(spec=vim.vm.device.VirtualEthernetCard),
                 'net 2': Mock(spec=vim.vm.device.VirtualEthernetCard)}
        network2 = Mock(spec=vim.Network)
        network2.name = 'aa'
        network1 = Mock(spec=vim.Network)
        network1.name = 'bb'
        request1 = ConnectRequest('net 2', 'aa')
        request2 = ConnectRequest(None, 'ab')
        requests = [request1, request2]
        mapper = VnicToNetworkMapper(DvPortGroupNameGenerator())
        mappig = mapper.map_request_to_vnics(requests, vnics, [], network1, [])
        self.assertTrue(mappig[request1.vnic_name], request1.network)
        self.assertTrue(mappig['net 1'], request2.network)
