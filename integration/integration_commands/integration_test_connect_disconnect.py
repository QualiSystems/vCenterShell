from unittest import TestCase

from mock import Mock
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim

from cloudshell.cp.vcenter.commands.disconnect_dvswitch import VirtualSwitchToMachineDisconnectCommand
from cloudshell.cp.vcenter.common.vcenter.task_waiter import SynchronousTaskWaiter
from cloudshell.cp.vcenter.common.vcenter.vmomi_service import pyVmomiService
from cloudshell.cp.vcenter.models.VCenterConnectionDetails import VCenterConnectionDetails
from cloudshell.cp.vcenter.network.dvswitch.name_generator import DvPortGroupNameGenerator
from cloudshell.cp.vcenter.network.vnic.vnic_service import VNicService
from cloudshell.cp.vcenter.vm.portgroup_configurer import *
from cloudshell.cp.vcenter.vm.vnic_to_network_mapper import VnicToNetworkMapper
from cloudshell.tests.utils.testing_credentials import TestCredentials


class TestVirtualSwitchToMachineConnector(TestCase):

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

        self.vm = None

        self.virtual_machine_path = 'SergiiT'
        self.virtual_machine_name = 'test_4f383119'
        self.vm_uuid = None

        self.vcenter_name = "QualiSB"
        self.dv_switch_path = 'QualiSB'
        self.network_path = 'QualiSB'

        #self.dv_switch_name = 'dvSwitch-SergiiT'
        self.dv_switch_name = 'dvSwitch'
        #self.dv_port_group_name = 'aa-dvPortGroup3B'
        self.dv_port_group_name = 'dvPortGroup'
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
            self.pg_name_generator = DvPortGroupNameGenerator
            self.vnic_to_network_mapper = VnicToNetworkMapper(self.pg_name_generator)

            self.configurer = VirtualMachinePortGroupConfigurer(self.py_vmomi_service,
                                                                self.synchronous_task_waiter,
                                                                self.vnic_to_network_mapper,
                                                                VNicService())
        except:
            print "Infrastructure not available - pretty OK or UnitTesting environment"

    def get_vm(self, py_vmomi_service, virtual_machine_name, si=None):
        if not self.vm:
            if not si:
                si = self.si
            self.vm = py_vmomi_service.get_obj(si.content, [vim.VirtualMachine], virtual_machine_name)
        return self.vm

    def get_vm_uuid(self, py_vmomi_service, virtual_machine_name, si=None):
        if not self.vm_uuid:
            self.vm_uuid = self.get_vm(py_vmomi_service, virtual_machine_name, si).config.uuid
        return self.vm_uuid

    def integrationtest_disconnect_all(self):
        default_network = None
        connector = VirtualSwitchToMachineDisconnectCommand(self.py_vmomi_service,
                                                            self.resource_connection_details_retriever,
                                                            self.configurer,
                                                            default_network)

        self.vm_uuid = self.vm_uuid or self.get_vm_uuid(self.py_vmomi_service, self.virtual_machine_name)
        print "DISCONNECT. Machine: '{}' UUID: [{}]".format(self.virtual_machine_name, self.vm_uuid)

        result = connector.disconnect_all(self.vcenter_name, self.vm_uuid)

        print result

    def test_integrationtest_disconnect(self):
        default_network = None
        connector = VirtualSwitchToMachineDisconnectCommand(self.py_vmomi_service,
                                                            self.configurer,
                                                            default_network)

        self.vm_uuid = self.vm_uuid or self.get_vm_uuid(self.py_vmomi_service, self.virtual_machine_name)
        print "DISCONNECT. Machine: '{}' UUID: [{}]".format(self.virtual_machine_name, self.vm_uuid)

        #result = connector.disconnect(self.vcenter_name, self.vm_uuid, self.dv_port_group_name)
        result = connector.disconnect(self.vcenter_name, self.vm_uuid, self.standard_network_name)

        print result


    def integrationtest_all_disconnect(self):
        default_network = None
        connector = VirtualSwitchToMachineDisconnectCommand(self.py_vmomi_service,
                                                            self.resource_connection_details_retriever,
                                                            self.configurer,
                                                            default_network)

        self.vm_uuid = self.vm_uuid or self.get_vm_uuid(self.py_vmomi_service, self.virtual_machine_name)
        print "DISCONNECT ALL. Machine: '{}' UUID: [{}]".format(self.virtual_machine_name, self.vm_uuid)
        result = connector.disconnect_all(self.vcenter_name, self.vm_uuid)
        print result


    def integrationtest_remove_interface(self):
        default_network = None
        connector = VirtualSwitchToMachineDisconnectCommand(self.py_vmomi_service,
                                                            self.resource_connection_details_retriever,
                                                            self.configurer,
                                                            default_network)

        vm = self.get_vm(self.py_vmomi_service, self.virtual_machine_name)
        print "Remove vNIC. Machine: '{}' UUID: [{}]".format(self.virtual_machine_name, self.vm_uuid)
        task = connector.remove_interfaces_from_vm_task(vm)
        self.synchronous_task_waiter.wait_for_task(task, Mock())


    def integrationtest_attach_vnic(self, network):
        nicspes = VNicService.vnic_new_attached_to_network(network)
        path = "{}/{}".format(self.vcenter_name, self.virtual_machine_path)
        vm = self.py_vmomi_service.find_vm_by_name(self.si, path, self.virtual_machine_name)
        if not vm:
            print "No VM named '{}/{}'".format(path, self.virtual_machine_name)
            return
        print "VM found. \n{}".format(vm)

        task = VNicService.vnic_add_to_vm_task(nicspes, vm)
        self.synchronous_task_waiter.wait_for_task(task, Mock())

    def integrationtest_attach_vnic_standard(self):
        network = self.py_vmomi_service.find_network_by_name(self.si, self.network_path, self.standard_network_name)
        return self.integrationtest_attach_vnic(network)

    def integrationtest_attach_vnic_portgroup(self):
        network = self.py_vmomi_service.find_network_by_name(self.si,
                                                             self.port_group_path,
                                                             self.dv_port_group_name)
        if not network:
            print "No Network '{}'".format(network)
            return
        return self.integrationtest_attach_vnic(network)

    def port_group_destroy(self):
        port_group = self.py_vmomi_service.find_network_by_name(self.si, self.port_group_path, self.dv_port_group_name)

        task = DvPortGroupCreator.dv_port_group_destroy_task(port_group)
        print task
        # print_attributes(task)
        try:
            self.synchronous_task_waiter.wait_for_task(task, Mock())
        except vim.fault.ResourceInUse, e:
            print "IT USED NOW"
        pass

    def test_integration(self):
        # self.integrationtest_attach_vnic()
        #self.integrationtest_connect()
        #self.integrationtest_disconnect()
        #self.integrationtest_all_disconnect()
        #self.integrationtest_remove_interface()
        # self.integrationtest_attach_vnic()
        #self.integrationtest_attach_vnic_portgroup()
        self.integrationtest_attach_vnic_portgroup()
        #self.integrationtest_attach_vnic_portgroup()

        #self.integrationtest_attach_vnic_standard()
        print "Integration Testing COMPLETED"
        # self.port_group_destroy()
        pass
