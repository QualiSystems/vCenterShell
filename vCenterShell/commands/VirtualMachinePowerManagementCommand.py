from pycommon.logger import getLogger

_logger = getLogger("vCenterShell")


class VirtualMachinePowerManagementCommand(object):
    def __init__(self,
                 pyvmomi_service,
                 connection_retriever,
                 synchronous_task_waiter):
        self.pyvmomi_service = pyvmomi_service
        self.connection_retriever = connection_retriever
        self.synchronous_task_waiter = synchronous_task_waiter

    def _connect_to_vcenter(self, vcenter_name):
        """
        connects to the specified vCenter
        :param str vcenter_name: the name of the vcenter to connect
        :rtype vim.ServiceInstance: si
        """
        connection_details = self.connection_retriever.connection_details(vcenter_name)

        si = self.pyvmomi_service.connect(connection_details.host,
                                          connection_details.username,
                                          connection_details.password,
                                          connection_details.port)
        return si

    def power_off(self, vcenter_name, vm_uuid):
        """
        hard power of the specified on the vcenter
        :param vcenter_name: vcenter name
        :param vm_uuid: the uuid of the vm
        :return:
        """
        si = self._connect_to_vcenter(vcenter_name)
        _logger.debug("Revoking ALL Interfaces from VM '{}'".format(vm_uuid))

        vm = self._get_vm(si, vm_uuid)

        # hard power off
        task = vm.PowerOff()
        return self.synchronous_task_waiter.wait_for_task(task)

    def power_on(self, vcenter_name, vm_uuid):
        """
        power on the specified vm
        :param vcenter_name: vcenter name
        :param vm_uuid: the uuid of the vm
        :return:
        """
        si = self._connect_to_vcenter(vcenter_name)
        _logger.debug("Revoking ALL Interfaces from VM '{}'".format(vm_uuid))

        vm = self._get_vm(si, vm_uuid)
        task = vm.PowerOn()
        return self.synchronous_task_waiter.wait_for_task(task)

    def _get_vm(self, si, vm_uuid):
        vm = self.pyvmomi_service.find_by_uuid(si, vm_uuid)
        if vm is None:
            raise Exception('vm not found with the uuid:{0}'.format(vm_uuid))
        return vm
