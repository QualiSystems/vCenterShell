from common.logger import getLogger

_logger = getLogger("vCenterShell")


class VirtualMachinePowerManagementCommand(object):
    def __init__(self,
                 pyvmomi_service,
                 connection_retriever,
                 synchronous_task_waiter,
                 qualipy_helpers):
        self.pyvmomi_service = pyvmomi_service
        self.connection_retriever = connection_retriever
        self.synchronous_task_waiter = synchronous_task_waiter
        self.qualipy_helpers = qualipy_helpers

    def _connect_to_vcenter(self):
        """
        connects to the specified vCenter
        :rtype vim.ServiceInstance: si
        """
        # gets the name of the vcenter to connect
        resource_att = self.qualipy_helpers.get_resource_context_details()
        inventory_path_data = self.connection_retriever.getVCenterInventoryPathAttributeData(resource_att)
        vcenter_resource_name = inventory_path_data['vCenter_resource_name']

        connection_details = self.connection_retriever.connection_details(vcenter_resource_name)

        si = self.pyvmomi_service.connect(connection_details.host,
                                          connection_details.username,
                                          connection_details.password,
                                          connection_details.port)
        return si

    def power_off(self, vm_uuid):
        """
        hard power of the specified on the vcenter
        :param vcenter_name: vcenter name
        :param vm_uuid: the uuid of the vm
        :return:
        """
        _logger.info('connecting to vcenter')
        si = self._connect_to_vcenter()

        _logger.info('retrieving vm by uuid: {0}'.format(vm_uuid))
        vm = self._get_vm(si, vm_uuid)

        # hard power off
        _logger.info('hard powering of vm')
        task = vm.PowerOff()
        return self.synchronous_task_waiter.wait_for_task(task)

    def power_on(self, vm_uuid):
        """
        power on the specified vm
        :param vcenter_name: vcenter name
        :param vm_uuid: the uuid of the vm
        :return:
        """
        _logger.info('connecting to vcenter')
        si = self._connect_to_vcenter()

        _logger.info('retrieving vm by uuid: {0}'.format(vm_uuid))
        vm = self._get_vm(si, vm_uuid)

        _logger.info('powering on vm')
        task = vm.PowerOn()
        return self.synchronous_task_waiter.wait_for_task(task)

    def _get_vm(self, si, vm_uuid):
        vm = self.pyvmomi_service.find_by_uuid(si, vm_uuid)
        if vm is None:
            raise Exception('vm not found with the uuid:{0}'.format(vm_uuid))
        return vm
