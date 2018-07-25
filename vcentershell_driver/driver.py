from cloudshell.cp.core import DriverRequestParser
from cloudshell.cp.core.models import DeployApp, DriverResponse, SaveApp, DeleteSavedApp
from cloudshell.cp.core.utils import single

from cloudshell.cp.vcenter.commands.command_orchestrator import CommandOrchestrator
from cloudshell.shell.core.context import ResourceCommandContext, CancellationContext
from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface
from cloudshell.cp.vcenter.common.vcenter.model_auto_discovery import VCenterAutoModelDiscovery
from cloudshell.cp.vcenter.models.DeployFromTemplateDetails import DeployFromTemplateDetails


class VCenterShellDriver(ResourceDriverInterface):
    def cleanup(self):
        pass

    def __init__(self):
        """
        ctor must be without arguments, it is created with reflection at run time
        """
        self.request_parser = DriverRequestParser()
        self.command_orchestrator = CommandOrchestrator()  # type: CommandOrchestrator
        self.deployments = dict()
        self.deployments['vCenter Clone VM From VM'] = self.deploy_clone_from_vm
        self.deployments['VCenter Deploy VM From Linked Clone'] = self.deploy_from_linked_clone
        self.deployments['vCenter VM From Template'] = self.deploy_from_template
        self.deployments['vCenter VM From Image'] = self.deploy_from_image

    def initialize(self, **kwargs):
        pass

    def ApplyConnectivityChanges(self, context, request):
        return self.command_orchestrator.connect_bulk(context, request)

    def disconnect_all(self, context, ports):
        return self.command_orchestrator.disconnect_all(context, ports)

    def disconnect(self, context, ports, network_name):
        return self.command_orchestrator.disconnect(context, ports, network_name)

    def DeleteInstance(self, context, ports):
        return self.command_orchestrator.DeleteInstance(context, ports)

    def remote_refresh_ip(self, context, cancellation_context, ports):
        return self.command_orchestrator.refresh_ip(context, cancellation_context, ports)

    def PowerOff(self, context, ports):
        return self.command_orchestrator.power_off(context, ports)

    # the name is by the Qualisystems conventions
    def PowerOn(self, context, ports):
        """
        Powers off the remote vm
        :param models.QualiDriverModels.ResourceRemoteCommandContext context: the context the command runs on
        :param list[string] ports: the ports of the connection between the remote resource and the local resource, NOT IN USE!!!
        """
        return self.command_orchestrator.power_on(context, ports)

    # the name is by the Qualisystems conventions
    def PowerCycle(self, context, ports, delay):
        return self.command_orchestrator.power_cycle(context, ports, delay)

    def Deploy(self, context, request=None, cancellation_context=None):
        actions = self.request_parser.convert_driver_request_to_actions(request)
        deploy_action = single(actions, lambda x: isinstance(x, DeployApp))
        deployment_name = deploy_action.actionParams.deployment.deploymentPath

        if deployment_name in self.deployments.keys():
            deploy_method = self.deployments[deployment_name]
            deploy_result = deploy_method(context, deploy_action, cancellation_context)
            return DriverResponse([deploy_result]).to_driver_response_json()
        else:
            raise Exception('Could not find the deployment')

    def SaveApp(self, context, request, cancellation_context=None):
        actions = self.request_parser.convert_driver_request_to_actions(request)
        save_actions = [x for x in actions if isinstance(x, SaveApp)]
        save_app_results = self.command_orchestrator.save_sandbox(context, save_actions, cancellation_context)
        return DriverResponse(save_app_results).to_driver_response_json()

    def DeleteSavedApps(self, context, request, cancellation_context=None):
        actions = self.request_parser.convert_driver_request_to_actions(request)
        delete_actions = [x for x in actions if isinstance(x, DeleteSavedApp)]
        save_app_results = self.command_orchestrator.delete_saved_sandbox(context, delete_actions, cancellation_context)
        return DriverResponse(save_app_results).to_driver_response_json()

    def deploy_from_template(self, context, deploy_action, cancellation_context):
        return self.command_orchestrator.deploy_from_template(context, deploy_action, cancellation_context)

    def deploy_clone_from_vm(self, context, deploy_action, cancellation_context):
        return self.command_orchestrator.deploy_clone_from_vm(context, deploy_action, cancellation_context)

    def deploy_from_linked_clone(self, context, deploy_action, cancellation_context):
        return self.command_orchestrator.deploy_from_linked_clone(context, deploy_action, cancellation_context)

    def deploy_from_image(self, context, deploy_action, cancellation_context):
        if cancellation_context is None:
            cancellation_context = CancellationContext()
        return self.command_orchestrator.deploy_from_image(context, deploy_action, cancellation_context)

    def get_inventory(self, context):
        """
        :type context: models.QualiDriverModels.AutoLoadCommandContext
        """

        validator = VCenterAutoModelDiscovery()
        return validator.validate_and_discover(context)

    def remote_save_snapshot(self, context, ports, snapshot_name, save_memory):
        """
        Saves virtual machine to a snapshot
        :param context: resource context of the vCenterShell
        :type context: models.QualiDriverModels.ResourceCommandContext
        :param ports:list[string] ports: the ports of the connection between the remote resource and the local resource
        :type ports: list[string]
        :param snapshot_name: snapshot name to save to
        :type snapshot_name: str
        :param save_memory: Snapshot the virtual machine's memory. Lookup, Yes / No
        :type save_memory: str
        :return:
        """
        return self.command_orchestrator.save_snapshot(context, snapshot_name, save_memory)

    def remote_restore_snapshot(self, context, ports, snapshot_name):
        """
        Restores virtual machine from a snapshot
        :param context: resource context of the vCenterShell
        :type context: models.QualiDriverModels.ResourceCommandContext
        :param ports:list[string] ports: the ports of the connection between the remote resource and the local resource
        :type ports: list[string]
        :param snapshot_name: Snapshot name to restore from
        :type snapshot_name: str
        :return:
        """
        return self.command_orchestrator.restore_snapshot(context, snapshot_name)

    def remote_get_snapshots(self, context, ports):
        """
        Returns list of snapshots
        :param context: resource context of the vCenterShell
        :type context: models.QualiDriverModels.ResourceCommandContext
        :param ports:list[string] ports: the ports of the connection between the remote resource and the local resource
        :type ports: list[string]
        :return: list
        """
        return self.command_orchestrator.get_snapshots(context)

    def orchestration_save(self, context, ports, mode="shallow", custom_params=None):
        return self.command_orchestrator.orchestration_save(context, mode, custom_params)

    def orchestration_restore(self, context, ports, saved_details):
        return self.command_orchestrator.orchestration_restore(context, saved_details)

    def get_vm_uuid(self, context, vm_name):
        return self.command_orchestrator.get_vm_uuid_by_name(context, vm_name)

    def GetVmDetails(self, context, cancellation_context, requests):
        return self.command_orchestrator.get_vm_details(context, cancellation_context, requests)
