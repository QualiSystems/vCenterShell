from cloudshell.cp.vcenter.common.vcenter.task_waiter import SynchronousTaskWaiter
from cloudshell.cp.vcenter.common.vcenter.vmomi_service import pyVmomiService
from cloudshell.cp.core.models import SaveApp
from cloudshell.cp.vcenter.models.vCenterCloneVMFromVMResourceModel import vCenterCloneVMFromVMResourceModel
from cloudshell.cp.vcenter.models.DeployFromTemplateDetails import DeployFromTemplateDetails
from cloudshell.cp.core.utils import convert_attributes_list_to_dict as convert_to_dict
from contextlib import contextmanager


class SaveAppCommand:
    def __init__(self, pyvmomi_service, task_waiter, deployer, resource_model_parser, snapshot_saver):
        """
        :param pyvmomi_service:
        :type pyvmomi_service: pyVmomiService
        :param task_waiter: Waits for the task to be completed
        :type task_waiter:  SynchronousTaskWaiter
        """
        self.pyvmomi_service = pyvmomi_service
        self.task_waiter = task_waiter
        self.deployer = deployer
        self.resource_model_parser = resource_model_parser
        self.snapshot_saver = snapshot_saver

    def save_app(self, si, logger, vcenter_data_model, reservation_id, save_app_actions, cancellation_context):
        """
        Cretaes an artifact of an app, that can later be restored

        :param vim.ServiceInstance si: py_vmomi service instance
        :type si: vim.ServiceInstance
        :param logger: Logger
        :type logger: cloudshell.core.logger.qs_logger.get_qs_logger
        :param list[SaveApp] save_app_actions:
        :param cancellation_context:
        """

        if not save_app_actions:
            raise Exception('Failed to save app, missing data in request.')

        for save in save_app_actions:
            # handle cancellation
            # get source vm for saving app
            app_saver = ArtifactSaver.factory(save, self.pyvmomi_service, vcenter_data_model, si, logger, self.deployer,
                                              reservation_id, self.resource_model_parser, self.snapshot_saver)
            app_saver.save(cancellation_context)
        return


class ArtifactSaver(object):
    @staticmethod
    def factory(save_action, pv_service, vcenter_data_model, si, logger, deployer, reservation_id,
                resource_model_parser, snapshot_saver):
        if save_action.actionParams.savedType == 'linkedClone':
            return LinkedCloneArtifactSaver(save_action, pv_service, vcenter_data_model, si, logger, deployer,
                                            reservation_id, resource_model_parser, snapshot_saver)
        raise Exception('Artifact save type not supported')


class LinkedCloneArtifactSaver(object):
    def __init__(self, save_action, pv_service, vcenter_data_model, si, logger, deployer, reservation_id,
                 resource_model_parser, snapshot_saver, task_waiter):
        self.save_action = save_action
        self.pv_service = pv_service
        self.vcenter_data_model = vcenter_data_model
        self.si = si
        self.logger = logger
        self.deployer = deployer
        self.reservation_id = reservation_id
        deploy_from_vm_model = resource_model_parser.convert_to_resource_model(
            attributes=save_action.actionParams.appAttributes,
            resource_model_type=vCenterCloneVMFromVMResourceModel)
        self.data_holder = DeployFromTemplateDetails(deploy_from_vm_model, save_action.actionParams.sourceVmUuid)  # todo: change name for cloned vm!
        self.snapshot_saver = snapshot_saver
        self.task_waiter = task_waiter
        # self.data_holder.template_resource_model.vm_location

    def save(self, cancellation_context):
        save_attributes = convert_to_dict(self.save_action.actionParams.appAttributes)

        # If the behavior during save is power off, we will power off VMs and then power on after clone
        power_off_during_clone = save_attributes.get("Behavior during save") == "Power Off"

        with self.manage_power_during_save(self.save_action.actionParams.sourceVmUuid, power_off_during_clone):
            result = self.deployer.deploy_clone_from_vm(self.si,
                                                        self.logger,
                                                        self.data_holder,
                                                        self.vcenter_data_model,
                                                        self.reservation_id,
                                                        cancellation_context)

        self.snapshot_saver.save_snapshot(self.si, self.logger, result.vmUuid,
                                          snapshot_name="artifact", save_memory=False)
        # save_snapshot should indicate by live status that process is occurring + activity feed

    @contextmanager
    def manage_power_during_save(self, vm_uuid, power_off_during_clone):
        if power_off_during_clone:
            vm = self.pv_service.find_by_uuid(self.si,vm_uuid)
            vm_started_as_powered_on = vm.summary.runtime.powerState == 'poweredOn'
            if vm_started_as_powered_on:
                task = vm.PowerOff()
                self.task_waiter.wait_for_task(task, self.logger, 'Power Off')
            yield
            # power on vm_uuid -> if not originally powered off
            if vm_started_as_powered_on:
                task = vm.PowerOn()
                self.task_waiter.wait_for_task(task, self.logger, 'Power Off')
        yield
