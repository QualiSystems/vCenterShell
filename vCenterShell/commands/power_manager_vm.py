from common.logger import getLogger

_logger = getLogger("vCenterShell")


class VirtualMachinePowerManagementCommand(object):
    def __init__(self,
                 pyvmomi_service,
                 synchronous_task_waiter):
        self.pyvmomi_service = pyvmomi_service
        self.synchronous_task_waiter = synchronous_task_waiter

    def power_off(self, si, vm_uuid):
        """
        hard power of the specified on the vcenter
        :param si: Service Instance
        :param vcenter_name: vcenter name
        :param vm_uuid: the uuid of the vm
        :return:
        """

        _logger.info('retrieving vm by uuid: {0}'.format(vm_uuid))
        vm = self.pyvmomi_service.find_by_uuid(si, vm_uuid)

        # hard power off
        _logger.info('hard powering of vm')
        task = vm.PowerOff()
        return self.synchronous_task_waiter.wait_for_task(task)

    def power_on(self, si, vm_uuid):
        """
        power on the specified vm
        :param vcenter_name: vcenter name
        :param vm_uuid: the uuid of the vm
        :return:
        """
        _logger.info('retrieving vm by uuid: {0}'.format(vm_uuid))
        vm = self.pyvmomi_service.find_by_uuid(si, vm_uuid)

        _logger.info('powering on vm')
        task = vm.PowerOn()
        return self.synchronous_task_waiter.wait_for_task(task)
