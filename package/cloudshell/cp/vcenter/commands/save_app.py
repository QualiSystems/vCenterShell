
from cloudshell.cp.vcenter.common.vcenter.task_waiter import SynchronousTaskWaiter
from cloudshell.cp.vcenter.common.vcenter.vmomi_service import pyVmomiService
from cloudshell.cp.core.models import SaveApp
from cloudshell.cp.vcenter.models.vCenterCloneVMFromVMResourceModel import vCenterCloneVMFromVMResourceModel
from cloudshell.cp.vcenter.models.DeployFromTemplateDetails import DeployFromTemplateDetails
from cloudshell.cp.core.utils import convert_attributes_list_to_dict as convert_to_dict
from contextlib import contextmanager
from itertools import groupby
from debug_utils import debugger


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

        actions_grouped_by_save_types = groupby(save_app_actions, lambda x: x.actionParams.savedType)
        artifactSaversToActions = {ArtifactSaver.factory(k,
                                                         self.pyvmomi_service,
                                                         vcenter_data_model,
                                                         si,
                                                         logger,
                                                         self.deployer,
                                                         reservation_id,
                                                         self.resource_model_parser,
                                                         self.snapshot_saver,
                                                         self.task_waiter): list(g)
                                   for k, g in actions_grouped_by_save_types}

        for artifactSaver in artifactSaversToActions.keys():
            save_actions = artifactSaversToActions[artifactSaver]
            for action in save_actions:
                artifactSaver.save(save_action=action, cancellation_context=cancellation_context)
        return


class ArtifactSaver(object):
    @staticmethod
    def factory(savedType, pv_service, vcenter_data_model, si, logger, deployer, reservation_id,
                resource_model_parser, snapshot_saver, task_waiter):
        if savedType == 'linkedClone':
            return LinkedCloneArtifactSaver(pv_service, vcenter_data_model, si, logger, deployer, reservation_id,
                                            resource_model_parser, snapshot_saver, task_waiter)
        raise Exception('Artifact save type not supported')


# todo interface for save from base
class LinkedCloneArtifactSaver(object):
    def __init__(self, pv_service, vcenter_data_model, si, logger, deployer, reservation_id,
                 resource_model_parser, snapshot_saver, task_waiter):
        debugger.attach_debugger()
        self.pv_service = pv_service
        self.vcenter_data_model = vcenter_data_model
        self.si = si
        self.logger = logger
        self.deployer = deployer
        self.reservation_id = reservation_id
        self.snapshot_saver = snapshot_saver
        self.task_waiter = task_waiter
        self.resource_model_parser = resource_model_parser

    def save(self, save_action, cancellation_context):
        # todo folderService (which will also handle locks)
        # todo: make sure vm location exists when saving
        data_holder = self.prepare_vm_data_holder(save_action)

        saved_sandbox_id = save_action.actionParams.savedSandboxId

        self.prepare_cloned_vm_vcenter_folder_structure(data_holder, saved_sandbox_id)

        self.update_cloned_vm_target_location(data_holder, saved_sandbox_id)

        with self.manage_power_during_save(save_action):
            result = self.deployer.deploy_clone_from_vm(self.si,
                                                        self.logger,
                                                        data_holder,
                                                        self.vcenter_data_model,
                                                        self.reservation_id,
                                                        cancellation_context)

        self.snapshot_saver.save_snapshot(self.si, self.logger, result.vmUuid,
                                          snapshot_name="artifact", save_memory='Nope')

    def prepare_vm_data_holder(self, save_action):
        deploy_from_vm_model = self.resource_model_parser.convert_to_resource_model(
            attributes=save_action.actionParams.appAttributes,
            resource_model_type=vCenterCloneVMFromVMResourceModel)
        data_holder = DeployFromTemplateDetails(deploy_from_vm_model,
                                                save_action.actionParams.sourceVmUuid)  # todo: change name for cloned vm!
        return data_holder

    @contextmanager
    def manage_power_during_save(self, save_action):
        # https://jeffknupp.com/blog/2016/03/07/python-with-context-managers/

        save_attributes = save_action.actionParams.appAttributes
        power_off_during_clone = save_attributes.get("Behavior during save") == "Power Off"
        source_vm_uuid = save_action.actionParams.sourceVmUuid

        if power_off_during_clone:
            vm = self.pv_service.find_by_uuid(self.si, source_vm_uuid)
            vm_started_as_powered_on = vm.summary.runtime.powerState == 'poweredOn'
            if vm_started_as_powered_on:
                task = vm.PowerOff()
                self.task_waiter.wait_for_task(task, self.logger, 'Power Off')

            yield

            # power on vm_uuid -> if not originally powered off
            if vm_started_as_powered_on:
                task = vm.PowerOn()
                self.task_waiter.wait_for_task(task, self.logger, 'Power Off')

        else:
            yield
