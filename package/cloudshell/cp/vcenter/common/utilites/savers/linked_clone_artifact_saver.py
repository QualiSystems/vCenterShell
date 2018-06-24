import threading
from contextlib import contextmanager
from itertools import groupby
from threading import Lock

from cloudshell.cp.core.models import Artifact, SaveAppResult, Attribute

from cloudshell.cp.vcenter.common.vcenter.vm_location import VMLocation
from cloudshell.cp.vcenter.models.DeployFromTemplateDetails import DeployFromTemplateDetails
from cloudshell.cp.vcenter.models.vCenterCloneVMFromVMResourceModel import vCenterCloneVMFromVMResourceModel
from cloudshell.cp.vcenter.vm.vcenter_details_factory import VCenterDetailsFactory


SAVED_SANDBOXES = "Saved Sandboxes"


class LinkedCloneArtifactHandler(object):
    def __init__(self, pv_service, vcenter_data_model, si, logger, deployer, reservation_id,
                 resource_model_parser, snapshot_saver, task_waiter, folder_manager, port_configurer):
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
        self.pg_configurer = port_configurer

    def save(self, save_action, cancellation_context):
        thread_id = threading.current_thread().ident
        self.logger.info('[{0}] Starting Save Action \nSource type: Linked Clone'.format(thread_id))

        vm = self._get_source_vm(save_action)
        self._add_clone_vm_source_to_deployment_attributes(save_action, vm)

        data_holder = self._prepare_vm_data_holder(save_action, self.vcenter_data_model)

        saved_sandbox_id = save_action.actionParams.savedSandboxId

        self._prepare_cloned_vm_vcenter_folder_structure(data_holder, saved_sandbox_id)

        self._update_cloned_vm_target_location(data_holder, saved_sandbox_id)

        if self.vcenter_data_model.saved_sandbox_storage:
            data_holder.template_resource_model.vm_storage = self.vcenter_data_model.saved_sandbox_storage

        with self._manage_power_during_save(save_action):
            self.logger.info('[{0}] Save sandbox - Creating Source VM'.format(thread_id))

            self.logger.info('[{0}] Copying existing sandbox app to create saved app source: \nOriginal app: {1}'.format(thread_id, data_holder.template_resource_model.vcenter_vm))

            result = self.deployer.deploy_clone_from_vm(self.si,
                                                        self.logger,
                                                        data_holder,
                                                        self.vcenter_data_model,
                                                        self.reservation_id,
                                                        cancellation_context)

        self._disconnect_all_quali_created_networks(result)

        self.logger.info('[{1}] Successfully cloned an app from sandbox to saved sandbox - saved sandbox id: {0}'.format(saved_sandbox_id, thread_id))
        self.logger.info('[{2}] Saved Sandbox App will clone from VM: {0}\n{1}'.format(result.vmUuid, result.vmName, thread_id))

        self.snapshot_saver.save_snapshot(self.si, self.logger, result.vmUuid,
                                          snapshot_name=self.SNAPSHOT_NAME, save_memory='Nope')

        self.logger.info('Saved snapshot on {0}'.format(result.vmName))

        save_artifact = Artifact(artifactId=result.vmUuid, artifactName=result.vmName)

        vcenter_vm_path = '/'.join([data_holder.template_resource_model.vm_location, result.vmName])
        saved_entity_attributes = [Attribute('vCenter VM', vcenter_vm_path),
                                   Attribute('vCenter VM Snapshot', self.SNAPSHOT_NAME)]

        self.logger.info('[{1}] Save Action using source type: Linked Clone Successful. Saved Sandbox App with snapshot created: {0}'.format(result.vmName, thread_id))

        return SaveAppResult(save_action.actionId,
                             True,
                             artifacts=[save_artifact],
                             savedEntityAttributes=saved_entity_attributes)

    def delete(self, delete_saved_app_actions, cancellation_context):
        sandbox_id_to_delete_actions = groupby(delete_saved_app_actions, lambda x: x.actionParams.savedSandboxId)
        for sandbox_id in sandbox_id_to_delete_actions:
            self._get_saved_sandbox_id_full_path(self.)

    def destroy(self, save_action):
        thread_id = threading.current_thread().ident

        self.logger.info('[{0}] Rollback initiated'.format(thread_id))
        saved_sandbox_path = self._get_saved_sandbox_path(save_action)

        try:
            self.folder_manager.delete_folder(self.si, self.logger, saved_sandbox_path)
        except:
            self.logger.info('Rollback for save_action {0} failed'.format(save_action.actionId))

        self.logger.info('Rollback for save_action {0} successful'.format(save_action.actionId))

    def _disconnect_all_quali_created_networks(self, result):
        thread_id = threading.current_thread().ident
        self.logger.info('{0} clearing networks configured by cloudshell on saved sandbox source app {1}'.format(thread_id, result.vmName))
        network_full_name = VMLocation.combine([self.vcenter_data_model.default_datacenter, self.vcenter_data_model.holding_network])
        self.logger.info('{0} Holding network is {1}'.format(thread_id, network_full_name))
        default_network = self.pv_service.get_network_by_full_name(self.si, network_full_name)
        vm = self.pv_service.get_vm_by_uuid(self.si, result.vmUuid)
        self.pg_configurer.disconnect_all_networks_if_created_by_quali(vm,
                                                                       default_network,
                                                                       self.vcenter_data_model.reserved_networks,
                                                                       self.logger)

    def _get_source_vm(self, save_action):
        vm_uuid = save_action.actionParams.sourceVmUuid
        could_not_save_artifact_message = 'Could not find VM with uuid {0}. \nCould not save artifact'.format(vm_uuid)
        try:
            self.logger.info('Looking for VM with uuid: {0}'.format(vm_uuid))
            vm = self.pv_service.get_vm_by_uuid(self.si, vm_uuid)
            if not vm:
                raise Exception(could_not_save_artifact_message)
        except:
            self.logger.exception(could_not_save_artifact_message)
            raise Exception(could_not_save_artifact_message)

        return vm

    def _get_saved_sandbox_path(self, save_action):
        data_holder = self._prepare_vm_data_holder(save_action, self.vcenter_data_model)
        saved_sandbox_id = save_action.actionParams.savedSandboxId
        return self._get_saved_sandbox_id_full_path(data_holder, saved_sandbox_id)

    def _get_saved_sandbox_id_full_path(self, data_holder, saved_sandbox_id):
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

    def _add_clone_vm_source_to_deployment_attributes(self, save_action, vm):
        attributes = save_action.actionParams.deploymentPathAttributes
        vm_full_path = self.pv_service.get_vm_full_path(self.si, vm)
        save_action.actionParams.deploymentPathAttributes['vCenter VM'] = vm_full_path
        return attributes

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
        behavior_during_save = save_attributes.get("Behavior during save") or self.vcenter_data_model.behavior_during_save
        power_off_during_clone = behavior_during_save == "Power Off"
        return power_off_during_clone
