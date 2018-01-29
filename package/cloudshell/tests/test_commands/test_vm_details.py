from unittest import TestCase
from mock import Mock

from cloudshell.cp.vcenter.commands.vm_details import VmDetailsCommand
from cloudshell.cp.vcenter.vm.vm_details_provider import VmDetailsProvider


class TestVmDetailsCommand(TestCase):
    def test(self):
        # ARRANGE
        vm = self.mock_vm()
        si = Mock()
        pyvmomi_service = Mock()
        pyvmomi_service.find_by_uuid = Mock(return_value=vm)
        param = Mock()
        param.name = 'ip_regex'
        param.value = 'bla.*'
        request = Mock()
        request.deployedAppJson.name = 'App1'
        request.deployedAppJson.vmdetails.vmCustomParams = [param]
        request.appRequestJson.deploymentService.model = 'vCenter Clone VM From VM'
        request.appRequestJson.deploymentService.attributes = [Mock()]
        resource_context = Mock()
        resource_context.attributes = {'Reserved Networks': 'Net1;B'}
        cancellation_context = Mock(is_cancelled=False)
        ip_manager = Mock()
        vm_details_provider = VmDetailsProvider(ip_manager)
        # ACT
        command = VmDetailsCommand(pyvmomi_service, vm_details_provider)
        datas = command.get_vm_details(
            si=si,
            logger=Mock(),
            resource_context=resource_context,
            requests=[request],
            cancellation_context=cancellation_context)
        # ASSERT
        self.assertEqual(len(datas), 1)
        data = datas[0]
        self.assertEqual(data.app_name, 'App1')
        self.assertEqual(data.error, None)
        self.assertEqual(len(data.vm_instance_data), 6)
        self.assertEqual(next(x.value for x in data.vm_instance_data if x.key == 'Cloned VM Name'), '')
        self.assertEqual(next(x.value for x in data.vm_instance_data if x.key == 'Current Snapshot'), 'Snap1')
        self.assertEqual(next(x.value for x in data.vm_instance_data if x.key == 'CPU'), '4 vCPU')
        self.assertEqual(next(x.value for x in data.vm_instance_data if x.key == 'Memory'), '2 GB')
        self.assertEqual(next(x.value for x in data.vm_instance_data if x.key == 'Disk Size'), '0 KB')
        self.assertEqual(next(x.value for x in data.vm_instance_data if x.key == 'Guest OS'), 'Centos')

        self.assertEqual(len(data.vm_network_data), 1)
        nic = data.vm_network_data[0]
        self.assertEqual(nic.interface_id, 'Mac1')
        self.assertEqual(nic.is_predefined, True)
        self.assertEqual(nic.is_primary, False)
        self.assertEqual(nic.network_id, '65')

        self.assertEqual(len(nic.network_data), 4)
        self.assertEqual(next(x.value for x in nic.network_data if x.key == 'IP'), '1.2.3.4')
        self.assertEqual(next(x.value for x in nic.network_data if x.key == 'MAC Address'), 'Mac1')
        self.assertEqual(next(x.value for x in nic.network_data if x.key == 'Network Adapter'), 'NetDeviceLabel')
        self.assertEqual(next(x.value for x in nic.network_data if x.key == 'Port Group Name'), 'Net1')

    def mock_vm(self):
        vm = Mock()
        vm.summary.config.memorySizeMB = 2 * 1024
        # disk = vim.vm.device.VirtualDisk
        # disk.capacityInKB = 20 * 1024 * 1024
        vm.config.hardware.device = [Mock(key='1'), Mock(key='2', deviceInfo=Mock(label='NetDeviceLabel'))]
        vm.summary.config.numCpu = 4
        vm.summary.config.guestFullName = 'Centos'
        node = Mock()
        node.snapshot = Mock()
        node.name = 'Snap1'
        vm.snapshot.rootSnapshotList = [node]  # [Mock(snapshot=snapshot,name=Mock(return_value='Snap1'))]
        vm.snapshot.currentSnapshot = node.snapshot
        vm.guest.net = [Mock(network='Net1', ipAddress=['1.2.3.4'], macAddress='Mac1', deviceConfigId='2')]
        network = Mock()
        network.name = 'Net1'
        network.config.defaultPortConfig.vlan.vlanId = '65'
        vm.network = [network]
        return vm

        # def integration(self):
        #     credentials = TestCredentials()
        #     py_vmomi_service = pyVmomiService(connect=SmartConnect, disconnect=Disconnect,
        #                                       task_waiter=SynchronousTaskWaiter())
        #     si = py_vmomi_service.connect(credentials.host, credentials.username, credentials.password)
        #
        #     vm_details_provider = VmDetailsProvider(VMIPManager())
        #     cancel = Mock()
        #     cancel.is_cancelled = False
        #     logger = Mock()
        #     resource_context = Mock()
        #     resource_context.attributes = {'Reserved Networks': 'A'}
        #     requests = [Mock()]
        #     requests[0].deployedAppJson = Mock()
        #     requests[0].deployedAppJson.name = 'SomeApp'
        #     requests[0].deployedAppJson.vmdetails = Mock()
        #     requests[0].deployedAppJson.vmdetails.uid = '423283e4-0003-6e04-07bb-7e4c3ebcf993'
        #     requests[0].deployedAppJson.vmdetails.vmCustomParams = []
        #     requests[0].appRequestJson = Mock()
        #     requests[0].appRequestJson.deploymentService = Mock()
        #     requests[0].appRequestJson.deploymentService.model = 'vCenter Clone VM From VM'
        #     requests[0].appRequestJson.deploymentService.attributes = [Mock()]
        #
        #     vm = py_vmomi_service.find_by_uuid(si, '423283e4-0003-6e04-07bb-7e4c3ebcf993')
        #
        #     cmd = VmDetailsCommand(py_vmomi_service, vm_details_provider)
        #     d = cmd.get_vm_details(si, logger, resource_context, requests, cancel)
        #     # d = cmd.get_vm_details_by_vm_uuid(si, '42328fd2-98ee-6563-bcf9-ab12af30df66')
        #
        #     pass
