from common.logger import getLogger
import qualipy.scripts.cloudshell_scripts_helpers as helpers

_logger = getLogger("vCenterShell")


class VirtualMachinePowerManagementCommand(object):
    def __init__(self, pyvmomi_service, synchronous_task_waiter):
        self.pyvmomi_service = pyvmomi_service
        self.synchronous_task_waiter = synchronous_task_waiter

    def power_off(self, si, vm_uuid, resource_fullname):
        """
        hard power of the specified on the vcenter
        :param si: Service Instance
        :param vcenter_name: vcenter name
        :param vm_uuid: the uuid of the vm
        :param resource_fullname: the full name of the deployed app resource
        :return:
        """

        _logger.info('retrieving vm by uuid: {0}'.format(vm_uuid))
        vm = self.pyvmomi_service.find_by_uuid(si, vm_uuid)

        if vm.summary.runtime.powerState == 'poweredOff':
            _logger.info('vm already powered off')
            task_result = 'already powered off'
        else:
            # hard power off
            _logger.info('hard powering of vm')
            task = vm.PowerOff()
            task_result = self.synchronous_task_waiter.wait_for_task(task=task,
                                                                     action_name='Power Off')

        # Set live status - deployment done
        if resource_fullname:
            helpers.get_api_session()\
                .SetResourceLiveStatus(resource_fullname, "Offline", "Powered Off")

        return task_result

    def power_on(self, si, vm_uuid, resource_fullname):
        """
        power on the specified vm
        :param vcenter_name: vcenter name
        :param vm_uuid: the uuid of the vm
        :param resource_fullname: the full name of the deployed app resource
        :return:
        """
        _logger.info('retrieving vm by uuid: {0}'.format(vm_uuid))
        vm = self.pyvmomi_service.find_by_uuid(si, vm_uuid)

        if vm.summary.runtime.powerState == 'poweredOn':
            _logger.info('vm already powered on')
            task_result = 'already powered on'
        else:
            _logger.info('powering on vm')
            task = vm.PowerOn()
            task_result = self.synchronous_task_waiter.wait_for_task(task=task,
                                                                     action_name='Power On')

        # Set live status - deployment done
        if resource_fullname:
            helpers.get_api_session()\
                .SetResourceLiveStatus(resource_fullname, "Online", "Active")

        return task_result
