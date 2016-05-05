

class VirtualMachinePowerManagementCommand(object):
    def __init__(self, pyvmomi_service, synchronous_task_waiter):
        """

        :param pyvmomi_service:
        :param synchronous_task_waiter:
        :type synchronous_task_waiter:  cloudshell.cp.vcenter.common.vcenter.task_waiter.SynchronousTaskWaiter
        :return:
        """
        self.pv_service = pyvmomi_service
        self.synchronous_task_waiter = synchronous_task_waiter

    def power_off(self, si, logger, session, vcenter_data_model, vm_uuid, resource_fullname):
        """
        Power off of a vm
        :param vcenter_data_model: vcenter model
        :param si: Service Instance
        :param logger:
        :param session:
        :param vcenter_data_model: vcenter_data_model
        :param vm_uuid: the uuid of the vm
        :param resource_fullname: the full name of the deployed app resource
        :return:
        """

        logger.info('retrieving vm by uuid: {0}'.format(vm_uuid))
        vm = self.pv_service.find_by_uuid(si, vm_uuid)

        if vm.summary.runtime.powerState == 'poweredOff':
            logger.info('vm already powered off')
            task_result = 'already powered off'
        else:
            # hard power off
            logger.info('{0} powering of vm'.format(vcenter_data_model.shutdown_method))
            if vcenter_data_model.shutdown_method.lower() != 'soft':
                task = vm.PowerOff()
                task_result = self.synchronous_task_waiter.wait_for_task(task=task,
                                                                         logger=logger,
                                                                         action_name='Power Off')
            else:
                if vm.guest.toolsStatus == 'toolsNotInstalled':
                    logger.warning('VMWare Tools status on virtual machine \'{0}\' are not installed'.format(vm.name))
                    raise ValueError('Cannot power off the vm softly because VMWare Tools are not installed')

                if vm.guest.toolsStatus == 'toolsNotRunning':
                    logger.warning('VMWare Tools status on virtual machine \'{0}\' are not running'.format(vm.name))
                    raise ValueError('Cannot power off the vm softly because VMWare Tools are not running')

                vm.ShutdownGuest()
                task_result = 'vm powered off'

        # Set live status - deployment done
        if resource_fullname:
            session.SetResourceLiveStatus(resource_fullname, "Offline", "Powered Off")

        return task_result

    def power_on(self, si, logger, session, vm_uuid, resource_fullname):
        """
        power on the specified vm
        :param si:
        :param logger:
        :param session:
        :param vm_uuid: the uuid of the vm
        :param resource_fullname: the full name of the deployed app resource
        :return:
        """
        logger.info('retrieving vm by uuid: {0}'.format(vm_uuid))
        vm = self.pv_service.find_by_uuid(si, vm_uuid)

        if vm.summary.runtime.powerState == 'poweredOn':
            logger.info('vm already powered on')
            task_result = 'already powered on'
        else:
            logger.info('powering on vm')
            task = vm.PowerOn()
            task_result = self.synchronous_task_waiter.wait_for_task(task=task,
                                                                     logger=logger,
                                                                     action_name='Power On')

        # Set live status - deployment done
        if resource_fullname:
            session.SetResourceLiveStatus(resource_fullname, "Online", "Active")

        return task_result
