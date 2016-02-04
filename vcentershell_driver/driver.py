from vCenterShell.commands.command_orchestrator import CommandOrchestrator


class VCenterShellDriver:
    def __init__(self):
        """
        ctor mast be without arguments, it is created with reflection at run time
        """
        self.command_orchestrator = None

    def initialize(self, context):
        self.command_orchestrator = CommandOrchestrator(context)

    def Connect(self, context, request):
        return self.command_orchestrator.connect_bulk(context, request)

    # obsolete
    def _connect(self, context, vm_uuid, vlan_id, vlan_spec_type):
        return self.command_orchestrator.connect(context, vm_uuid, vlan_id, vlan_spec_type)

    def disconnect_all(self, context, vm_uuid):
        return self.command_orchestrator.disconnect_all(context, vm_uuid)

    def disconnect(self, context, vm_uuid, network_name):
        return self.command_orchestrator.disconnect(context, vm_uuid, network_name)

    def destroy_vm(self, context, vm_uuid, resource_fullname):
        return self.command_orchestrator.destroy_vm(context, vm_uuid, resource_fullname)

    def deploy_from_template(self, context, deploy_data):
        return self.command_orchestrator.deploy_from_template(context, deploy_data)

    def power_off(self, context, vm_uuid, resource_fullname):
        return self.command_orchestrator.power_off(context, vm_uuid, resource_fullname)

    def power_on(self, context, vm_uuid, resource_fullname):
        return self.command_orchestrator.power_on(context, vm_uuid, resource_fullname)

    def refresh_ip(self, context, vm_uuid, resource_fullname):
        return self.command_orchestrator.refresh_ip(context, vm_uuid, resource_fullname)
