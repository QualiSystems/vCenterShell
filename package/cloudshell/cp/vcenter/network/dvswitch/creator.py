# -*- coding: utf-8 -*-
from threading import Lock

from pyVmomi import vim

from cloudshell.cp.vcenter.common.logger import getLogger

logger = getLogger("vCenterCommon")


class DvPortGroupCreator(object):
    def __init__(self, pyvmomi_service, synchronous_task_waiter):
        self.pyvmomi_service = pyvmomi_service
        self.synchronous_task_waiter = synchronous_task_waiter
        self._lock = Lock()

    def get_or_create_network(self,
                              si,
                              vm,
                              dv_port_name,
                              dv_switch_name,
                              dv_switch_path,
                              port_group_path,
                              vlan_id,
                              vlan_spec):
        network = None
        self._lock.acquire()
        try:
            # check if the network is attached to the vm and gets it, the function doesn't goes to the vcenter
            network = self.pyvmomi_service.get_network_by_name_from_vm(vm, dv_port_name)

            # if we didn't found the network on the vm
            if network is None:
                # try to get it from the vcenter
                try:
                    network = self.pyvmomi_service.find_network_by_name(si, dv_switch_path, dv_port_name)
                except KeyError:
                    network = None

            # if we still couldn't get the network ---> create it(can't find it, play god!)
            if network is None:
                self._create_dv_port_group(dv_port_name,
                                          dv_switch_name,
                                          dv_switch_path,
                                          si,
                                          vlan_spec,
                                          vlan_id)
                network = self.pyvmomi_service.find_network_by_name(si, dv_switch_path, dv_port_name)

        finally:
            self._lock.release()
            return network


    def _create_dv_port_group(self, dv_port_name, dv_switch_name, dv_switch_path, si, spec, vlan_id):
        dv_switch = self.pyvmomi_service.find_network_by_name(si, dv_switch_path, dv_switch_name)
        if dv_switch is None:
            raise Exception('DV Switch {0} not found in path {1}'.format(dv_switch_name, dv_switch_path))

        task = DvPortGroupCreator.dv_port_group_create_task(dv_port_name, dv_switch, spec, vlan_id)
        self.synchronous_task_waiter.wait_for_task(task=task,
                                                   action_name='Create dv port group')

    @staticmethod
    def dv_port_group_create_task(dv_port_name, dv_switch, spec, vlan_id, num_ports=32):
        """
        Create ' Distributed Virtual Portgroup' Task
        :param dv_port_name: <str>  Distributed Virtual Portgroup Name
        :param dv_switch: <vim.dvs.VmwareDistributedVirtualSwitch> Switch this Portgroup will be belong to
        :param spec:
        :param vlan_id: <int>
        :param num_ports: <int> number of ports in this Group
        :return: <vim.Task> Task which really provides update
        """

        dv_pg_spec = vim.dvs.DistributedVirtualPortgroup.ConfigSpec()
        dv_pg_spec.name = dv_port_name
        dv_pg_spec.numPorts = num_ports
        dv_pg_spec.type = vim.dvs.DistributedVirtualPortgroup.PortgroupType.earlyBinding

        dv_pg_spec.defaultPortConfig = vim.dvs.VmwareDistributedVirtualSwitch.VmwarePortConfigPolicy()
        dv_pg_spec.defaultPortConfig.securityPolicy = vim.dvs.VmwareDistributedVirtualSwitch.SecurityPolicy()

        dv_pg_spec.defaultPortConfig.vlan = spec
        dv_pg_spec.defaultPortConfig.vlan.vlanId = vlan_id
        dv_pg_spec.defaultPortConfig.securityPolicy.allowPromiscuous = vim.BoolPolicy(value=True)
        dv_pg_spec.defaultPortConfig.securityPolicy.forgedTransmits = vim.BoolPolicy(value=True)

        dv_pg_spec.defaultPortConfig.vlan.inherited = False
        dv_pg_spec.defaultPortConfig.securityPolicy.macChanges = vim.BoolPolicy(value=False)
        dv_pg_spec.defaultPortConfig.securityPolicy.inherited = False

        task = dv_switch.AddDVPortgroup_Task([dv_pg_spec])

        logger.info(u"DV Port Group '{}' CREATE Task ...".format(dv_port_name))
        return task

    @staticmethod
    def dv_port_group_destroy_task(port_group):
        """
        Creates 'Destroy Distributed Virtual Portgroup' Task
        The current Portgoriup should be 'Unused' if you wanted this task will be successfully performed
        :param port_group: <vim.dvs.DistributedVirtualPortgroup>
        :return: <vim.Task> Task which really provides update
        """
        return port_group.Destroy()

