from contextlib import contextmanager
from threading import Lock

from cloudshell.cp.core.models import Artifact, SaveAppResult, Attribute

from cloudshell.cp.vcenter.common.vcenter.vm_location import VMLocation
from cloudshell.cp.vcenter.models.DeployFromTemplateDetails import DeployFromTemplateDetails
from cloudshell.cp.vcenter.models.vCenterCloneVMFromVMResourceModel import vCenterCloneVMFromVMResourceModel
from cloudshell.cp.vcenter.vm.vcenter_details_factory import VCenterDetailsFactory


SAVED_SANDBOXES = "Saved Sandboxes"


# todo interface for save from base
class LinkedCloneArtifactSaver(object):
    def __init__(self, pv_service, vcenter_data_model, si, logger, deployer, reservation_id,
                 resource_model_parser, snapshot_saver, task_waiter, folder_manager):
        self.SNAPSHOT_NAME = 'artifact'
        self.saved_apps_folder_lock = Lock()
        self.saved_sandbox_folder_lock = Lock()
        self.pv_service = pv_service
        self.vcenter_data_model = vcenter_data_model
        self.si = si
        self.logger = logger
        self.deployer = deployer
        self.reservation_id = reservation_id
        self.snapshot_saver = snapshot_saver
        self.task_waiter = task_waiter
        self.resource_model_parser = resource_model_parser
        self.folder_manager = folder_manager

    def save(self, save_action, cancellation_context):
        self.logger.info('Saving artifact as linked clone')

        data_holder = self._prepare_vm_data_holder(save_action, self.vcenter_data_model)

        saved_sandbox_id = save_action.actionParams.savedSandboxId

        self._prepare_cloned_vm_vcenter_folder_structure(data_holder, saved_sandbox_id)

        self._update_cloned_vm_target_location(data_holder, saved_sandbox_id)

        if self.vcenter_data_model.saved_sandbox_storage:
            data_holder.template_resource_model.vm_storage = self.vcenter_data_model.saved_sandbox_storage

        with self._manage_power_during_save(save_action):
            result = self.deployer.deploy_clone_from_vm(self.si,
                                                        self.logger,
                                                        data_holder,
                                                        self.vcenter_data_model,
                                                        self.reservation_id,
                                                        cancellation_context)

        self.snapshot_saver.save_snapshot(self.si, self.logger, result.vmUuid,
                                          snapshot_name=self.SNAPSHOT_NAME, save_memory='Nope')

        save_artifact = Artifact(artifactId=result.vmUuid, artifactName=result.vmName)

        vcenter_vm_path = '/'.join([data_holder.template_resource_model.vm_location, result.vmName])
        saved_entity_attributes = [Attribute('vCenter VM', vcenter_vm_path),
                                   Attribute('vCenter VM Snapshot', self.SNAPSHOT_NAME)]

        return SaveAppResult(save_action.actionId,
                             True,
                             artifacts=[save_artifact],
                             savedEntityAttributes=saved_entity_attributes)

    def destroy(self, save_action):
        saved_sandbox_path = self._get_saved_sandbox_path(save_action)

        try:
            self.folder_manager.delete_folder(self.si, self.logger, saved_sandbox_path)
        except:
            self.logger.info('Rollback for save_action {0} failed'.format(save_action.actionId))

        self.logger.info('Rollback for save_action {0} successful'.format(save_action.actionId))

    def _get_saved_sandbox_path(self, save_action):
        data_holder = self._prepare_vm_data_holder(save_action, self.vcenter_data_model)
        saved_sandbox_id = save_action.actionParams.savedSandboxId
        saved_sandbox_path = VMLocation.combine(
            [data_holder.template_resource_model.vm_location, SAVED_SANDBOXES, saved_sandbox_id])
        return saved_sandbox_path

    def _update_cloned_vm_target_location(self, data_holder, saved_sandbox_id):
        data_holder.template_resource_model.vm_location = self._vcenter_sandbox_folder_path(saved_sandbox_id,
                                                                                            data_holder)

    def _prepare_cloned_vm_vcenter_folder_structure(self, data_holder, saved_sandbox_id):
        self._get_or_create_saved_apps_folder_in_vcenter(data_holder)
        self._get_or_create_saved_sandbox_folder(saved_sandbox_id, data_holder)

    def _prepare_vm_data_holder(self, save_action, vcenter_data_model):
        deploy_from_vm_model = self.resource_model_parser.convert_to_resource_model(
            save_action.actionParams.deploymentPathAttributes,
            vCenterCloneVMFromVMResourceModel)

        VCenterDetailsFactory.set_deplyment_vcenter_params(
            vcenter_resource_model=vcenter_data_model, deploy_params=deploy_from_vm_model)

        new_vm_name = self._generate_cloned_vm_name(save_action)

        data_holder = DeployFromTemplateDetails(deploy_from_vm_model, new_vm_name)
        return data_holder

    def _generate_cloned_vm_name(self, save_action):
        source_vm = self.pv_service.get_vm_by_uuid(self.si, save_action.actionParams.sourceVmUuid)
        if not source_vm:
            raise Exception('Source VM not found!')
        new_vm_name = ''.join(['Clone of ', source_vm.name])[0:32]
        return new_vm_name

    def _get_or_create_saved_sandbox_folder(self, saved_sandbox_id, data_holder):
        saved_apps_folder_path = '/'.join([data_holder.template_resource_model.vm_location, SAVED_SANDBOXES])
        self.folder_manager.get_or_create_vcenter_folder(self.si, self.logger, saved_apps_folder_path, saved_sandbox_id)

    def _vcenter_sandbox_folder_path(self, saved_sandbox_id, data_holder):
        vm_location = '/'.join(data_holder.template_resource_model.vm_location.split('/')[1:])
        return '/'.join([vm_location, SAVED_SANDBOXES, saved_sandbox_id])

    def _get_or_create_saved_apps_folder_in_vcenter(self, data_holder):
        root_path = data_holder.template_resource_model.vm_location
        return self.folder_manager.get_or_create_vcenter_folder(self.si, self.logger, root_path, SAVED_SANDBOXES)

    @contextmanager
    def _manage_power_during_save(self, save_action):
        # https://jeffknupp.com/blog/2016/03/07/python-with-context-managers/

        power_off_during_clone = self._should_vm_be_powered_off_during_clone(save_action)

        source_vm_uuid = save_action.actionParams.sourceVmUuid

        if power_off_during_clone:
            self.logger.info('Behavior during save: Power Off')
            vm = self.pv_service.find_by_uuid(self.si, source_vm_uuid)
            vm_started_as_powered_on = vm.summary.runtime.powerState == 'poweredOn'
            if vm_started_as_powered_on:
                task = vm.PowerOff()
                self.task_waiter.wait_for_task(task, self.logger, 'Power Off')

            yield

            # power on vm_uuid -> if not originally powered off
            if vm_started_as_powered_on:
                task = vm.PowerOn()
                self.task_waiter.wait_for_task(task, self.logger, 'Power On')

        else:
            yield

    def _should_vm_be_powered_off_during_clone(self, save_action):
        save_attributes = save_action.actionParams.deploymentPathAttributes
        behavior_during_save = save_attributes.get(
            "Behavior during save") or self.vcenter_data_model.behavior_during_save
        power_off_during_clone = behavior_during_save == "Power Off"
        return power_off_during_clone
