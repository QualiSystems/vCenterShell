import uuid
from unittest import TestCase
from mock import Mock, MagicMock
from pyVmomi import vim
from pyVim.connect import SmartConnect, Disconnect
from common.logger.service import LoggingService
from common.utilites.debug import print_attributes
from models.VCenterConnectionDetails import VCenterConnectionDetails
from tests.utils.testing_credentials import TestCredentials
from common.vcenter.task_waiter import SynchronousTaskWaiter
from vCenterShell.commands.disconnect_dvswitch import VirtualSwitchToMachineDisconnectCommand
from vCenterShell.network.vnic.vnic_service import VNicService
from vCenterShell.vm.portgroup_configurer import *



class TestVirtualSwitchToMachineConnector(TestCase):
    # LoggingService("CRITICAL", "DEBUG", None)
    LoggingService("DEBUG", "DEBUG", None)

    @property
    def si(self):
        if not self._si:
            credentials = self.credentials
            self._si = self.py_vmomi_service.connect(credentials.host,
                                                     credentials.username,
                                                     credentials.password,
                                                     credentials.port)
        return self._si

    def setUp(self):
        self._si = None

        self.virtual_machine_path = 'SergiiT'
        self.virtual_machine_name = 'JustTestNeedToBeRemoved'

        # hardcoded just for avoiding time spending for searching
        # vm_uuid = "4222ade0-f12e-3682-64f0-1bfe763605b1" # Boris
        self.vm_uuid = "422254d5-5226-946e-26fb-60c21898b731"  # Sergii
        # self.vm_uuid = None

        self.vcenter_name = "QualiSB"
        self.port_group_path = 'QualiSB'
        self.dv_switch_path = 'QualiSB'
        self.network_path = 'QualiSB'

        self.dv_switch_name = 'dvSwitch-SergiiT'
        # self.dv_port_group_name = 'aa-dvPortGroup2A'
        # self.dv_port_group_name = 'aa-dvPortGroup2A'
        self.dv_port_group_name = 'aa-dvPortGroup3B'

        self.standard_network_name = "Anetwork"
        try:
            self.py_vmomi_service = pyVmomiService(SmartConnect, Disconnect)
            self.credentials = TestCredentials()
            self.resource_connection_details_retriever = Mock()
            self.resource_connection_details_retriever.connection_details = Mock(
                return_value=VCenterConnectionDetails(self.credentials.host,
                                                      self.credentials.username,
                                                      self.credentials.password))

            self.synchronous_task_waiter = SynchronousTaskWaiter()
            self.virtual_machine_port_group_configurer = VirtualMachinePortGroupConfigurer(self.py_vmomi_service,
                                                                                           self.synchronous_task_waiter)
        except:
            print "Infrastructure not available - pretty OK or UnitTesting environment"
            pass

    def get_vm_uuid(self, py_vmomi_service, virtual_machine_name, si=None):
        if not si:
            si = self.si
        vm = py_vmomi_service.get_obj(si.content, [vim.VirtualMachine], virtual_machine_name)
        vm_uuid = vm.config.uuid
        return vm_uuid

    def integrationtest_disconnect_all(self):
        dv_port_group_configurer = VirtualMachinePortGroupConfigurer(self.py_vmomi_service,
                                                                     self.synchronous_task_waiter)
        connector = VirtualSwitchToMachineDisconnectCommand(self.py_vmomi_service,
                                                            self.resource_connection_details_retriever,
                                                            dv_port_group_configurer)

        self.vm_uuid = self.vm_uuid or self.get_vm_uuid(self.py_vmomi_service, self.virtual_machine_name)
        print "DISCONNECT. Machine: '{}' UUID: [{}]".format(self.virtual_machine_name, self.vm_uuid)

        result = connector.disconnect_all(self.vcenter_name, self.vm_uuid)

        print result

    def integrationtest_disconnect(self):
        dv_port_group_configurer = VirtualMachinePortGroupConfigurer(self.py_vmomi_service,
                                                                     self.synchronous_task_waiter)
        connector = VirtualSwitchToMachineDisconnectCommand(self.py_vmomi_service,
                                                            self.resource_connection_details_retriever,
                                                            dv_port_group_configurer)

        self.vm_uuid = self.vm_uuid or self.get_vm_uuid(self.py_vmomi_service, self.virtual_machine_name)
        print "DISCONNECT. Machine: '{}' UUID: [{}]".format(self.virtual_machine_name, self.vm_uuid)

        result = connector.disconnect(self.vcenter_name, self.vm_uuid, self.dv_port_group_name)

        print result

    # disconnect(self, vcenter_name, vm_uuid, network_name=None, default_network_full_name=None):

    def integrationtest_attach_vnic(self, network):
        nicspes = VNicService.vnic_new_attached_to_network(network)
        vm = self.py_vmomi_service.get_vm_by_uuid(self.si, self.vm_uuid)
        task = VNicService.vnic_add_to_vm_task(nicspes, vm)
        self.synchronous_task_waiter.wait_for_task(task)

    def integrationtest_attach_vnic_standard(self):
        network = self.py_vmomi_service.find_network_by_name(self.si, self.network_path, self.standard_network_name)
        return self.integrationtest_attach_vnic(network)

    def integrationtest_attach_vnic_portgroup(self):
        network = self.py_vmomi_service.find_network_by_name(self.si, self.port_group_path, self.dv_port_group_name)
        return self.integrationtest_attach_vnic(network)

    def port_group_destroy(self):
        port_group = self.py_vmomi_service.find_network_by_name(self.si, self.port_group_path, self.dv_port_group_name)

        task = DvPortGroupCreator.dv_port_group_destroy_task(port_group)
        print task
        # print_attributes(task)
        try:
            self.synchronous_task_waiter.wait_for_task(task)
        except vim.fault.ResourceInUse, e:
            print "IT USED NOW"
        pass

    def test_integration(self):
        # self.integrationtest_attach_vnic()
        #self.integrationtest_connect()
        # self.integrationtest_disconnect()
        # self.integrationtest_attach_vnic()
        # self.integrationtest_attach_vnic_portgroup()
        # self.integrationtest_attach_vnic_portgroup()
        # self.integrationtest_attach_vnic_portgroup()
        # self.integrationtest_attach_vnic_standard()
        print "Integration Testing COMPLETED"
        # self.port_group_destroy()
        pass
