from cloudshell.cp.vcenter.commands.command_orchestrator import CommandOrchestrator
from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface
from cloudshell.cp.vcenter.common.vcenter.model_auto_discovery import VCenterAutoModelDiscovery


class VCenterShellDriver (ResourceDriverInterface):

    def cleanup(self):
        pass

    def __init__(self):
        """
        ctor must be without arguments, it is created with reflection at run time
        """
        self.command_orchestrator = CommandOrchestrator()  # type: CommandOrchestrator

    def initialize(self):
        pass

    def ApplyConnectivityChanges(self, context, request):
        return self.command_orchestrator.connect_bulk(context, request)

    def disconnect_all(self, context, ports):
        return self.command_orchestrator.disconnect_all(context, ports)

    def disconnect(self, context, ports, network_name):
        return self.command_orchestrator.disconnect(context, ports, network_name)

    def destroy_vm_only(self, context, ports):
        return self.command_orchestrator.destroy_vm_only(context, ports)

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

    def deploy_from_template(self, context, deploy_data):
        return self.command_orchestrator.deploy_from_template(context, deploy_data)

    def deploy_clone_from_vm(self, context, deploy_data):
        return self.command_orchestrator.deploy_clone_from_vm(context, deploy_data)

    def deploy_from_linked_clone(self, context, deploy_data):
        return self.command_orchestrator.deploy_from_linked_clone(context, deploy_data)

    def deploy_from_image(self, context, deploy_data):
        return self.command_orchestrator.deploy_from_image(context, deploy_data)

    def get_inventory(self, context):
        """
        :type context: models.QualiDriverModels.AutoLoadCommandContext
        """

        validator = VCenterAutoModelDiscovery()
        return validator.validate_and_discover(context)

    def remote_save_snapshot(self, context, ports, snapshot_name):
        """
        Saves virtual machine to a snapshot
        :param context: resource context of the vCenterShell
        :type context: models.QualiDriverModels.ResourceCommandContext
        :param ports:list[string] ports: the ports of the connection between the remote resource and the local resource
        :type ports: list[string]
        :param snapshot_name: snapshot name to save to
        :type snapshot_name: str
        :return:
        """
        return self.command_orchestrator.save_snapshot(context, snapshot_name)

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

    def modify_vm_hardware(self, context, ports, vm_changes):
        """
        :param vm_changes: changes to CPU, memory or number of ethernet adapters - json string
        :type vm_changes: str
        """
        return self.command_orchestrator.modify_vm_hardware(context, vm_changes)
