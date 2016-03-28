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

    def destroy_vm(self, context, ports):
        return self.command_orchestrator.destroy_vm(context, ports)

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

    def deploy_from_image(self, context, deploy_data):
        return self.command_orchestrator.deploy_from_image(context, deploy_data)

    def get_inventory(self, context):
        """
        :type context: models.QualiDriverModels.AutoLoadCommandContext
        """

        validator = VCenterAutoModelDiscovery()
        return validator.validate_and_discover(context)



