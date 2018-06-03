from contextlib import contextmanager
from threading import Lock

from cloudshell.cp.core.models import Artifact, DataElement, SaveAppResult

from cloudshell.cp.vcenter.models.DeployFromTemplateDetails import DeployFromTemplateDetails
from cloudshell.cp.vcenter.models.vCenterCloneVMFromVMResourceModel import vCenterCloneVMFromVMResourceModel
from cloudshell.cp.vcenter.vm.vcenter_details_factory import VCenterDetailsFactory


# todo interface for save from base
class LinkedCloneArtifactSaver(object):
    def __init__(self, pv_service, vcenter_data_model, si, logger, deployer, reservation_id,
                 resource_model_parser, snapshot_saver, task_waiter):
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

    def save(self, save_action, cancellation_context):
        # todo folderService (which will also handle locks)

        self.logger.info('Saving artifact as linked clone')

        data_holder = self.prepare_vm_data_holder(save_action, self.vcenter_data_model)

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
                                          snapshot_name=self.SNAPSHOT_NAME, save_memory='Nope')

        save_artifact = Artifact(artifactId=result.vmUuid, artifactName=result.vmName)

        vcenter_vm = '/'.join(data_holder.template_resource_model.vm_location, result.vmName)
        saved_entity_attributes = {'vCenter VM': vcenter_vm,
                                   'vCenter VM Snapshot': self.SNAPSHOT_NAME}

        return SaveAppResult(save_action.actionId,
                             True,
                             artifacts=[save_artifact],
                             savedEntityAttributes=saved_entity_attributes)

    def update_cloned_vm_target_location(self, data_holder, saved_sandbox_id):
        data_holder.template_resource_model.vm_location = self._vcenter_sandbox_folder_path(saved_sandbox_id,
                                                                                            data_holder)

    def prepare_cloned_vm_vcenter_folder_structure(self, data_holder, saved_sandbox_id):
        saved_apps_folder = self._get_or_create_saved_apps_folder_in_vcenter(data_holder)
        self._get_or_create_saved_sandbox_folder(saved_apps_folder, saved_sandbox_id, data_holder)

    def prepare_vm_data_holder(self, save_action, vcenter_data_model):
        deploy_from_vm_model = self.resource_model_parser.convert_to_resource_model(
            save_action.actionParams.deploymentPathAttributes,
            vCenterCloneVMFromVMResourceModel)

        VCenterDetailsFactory.set_deplyment_vcenter_params(
            vcenter_resource_model=vcenter_data_model, deploy_params=deploy_from_vm_model)

        new_vm_name = self.generate_cloned_vm_name(save_action)

        data_holder = DeployFromTemplateDetails(deploy_from_vm_model, new_vm_name)
        return data_holder

    def generate_cloned_vm_name(self, save_action):
        source_vm = self.pv_service.get_vm_by_uuid(save_action.actionParams.sourceVmUuid)
        if not source_vm:
            raise Exception('Source VM not found!')
        new_vm_name = ''.join(['Clone of ', source_vm.name])[0:32]
        return new_vm_name

    def _get_or_create_saved_sandbox_folder(self, saved_apps_folder, saved_sandbox_id, data_holder):
        sandbox_path = '/'.join([data_holder.template_resource_model.vm_location, 'SavedApps', saved_sandbox_id])
        saved_sandbox_folder = self.pv_service.get_folder(self.si, sandbox_path)
        self.logger.info('Checking if saved sandbox folder {0} exists under SavedApps folder in vCenter'.format(saved_sandbox_id))
        if not saved_sandbox_folder:
            saved_apps_folder.CreateFolder(saved_sandbox_id)
            self.logger.info('Saved sandbox folder didn''t exist, was created.')

    def _vcenter_sandbox_folder_path(self, saved_sandbox_id, data_holder):
        vm_location = '/'.join(data_holder.template_resource_model.vm_location.split('/')[1:])
        return '/'.join([vm_location, 'SavedApps', saved_sandbox_id])

    def _get_or_create_saved_apps_folder_in_vcenter(self, data_holder):
        self.logger.info('Checking if SavedApps folder exists in VM Location: ' + data_holder.template_resource_model.vm_location)

        saved_apps_path = data_holder.template_resource_model.vm_location + '/' + "SavedApps"
        saved_apps_folder = self.pv_service.get_folder(self.si, saved_apps_path)
        if not saved_apps_folder:
            vm_location_path = data_holder.template_resource_model.vm_location

            self.logger.info('SavedApps folder not found, creating saved apps in path ' + vm_location_path)

            vm_location_folder = self.pv_service.get_folder(self.si, vm_location_path)
            saved_apps_folder = vm_location_folder.CreateFolder("SavedApps")

            self.logger.info('SavedApps folder created')
        return saved_apps_folder

    @contextmanager
    def manage_power_during_save(self, save_action):
        # https://jeffknupp.com/blog/2016/03/07/python-with-context-managers/

        save_attributes = save_action.actionParams.deploymentPathAttributes
        power_off_during_clone = save_attributes.get("Behavior during save") == "Power Off"
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