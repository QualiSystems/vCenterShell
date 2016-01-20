import qualipy.scripts.cloudshell_scripts_helpers as helpers
from qualipy.api.cloudshell_api import InputNameValue
from common.utilites.command_result import get_result_from_command_output, set_command_result
from common.logger import getLogger

_logger = getLogger('DeployedAppService')


#################################################
# === Should run under Deployed App context === #
#################################################


class DeployedAppService(object):
    def __init__(self, resource_model_parser):
        self.resource_model_parser = resource_model_parser
        self.resource_context = helpers.get_resource_context_details()
        self.generic_deployed_app_resource_model = self.resource_model_parser.convert_to_resource_model(
                self.resource_context)

    def connect(self):
        """
        Connect method should be executed on Deployed App
        It executes connect command on vCenter resource for each connected VLAN
        """
        vlan_spec_type = helpers.get_user_param('VLAN_SPEC_TYPE')

        if not vlan_spec_type:
            raise ValueError('VLAN_SPEC_TYPE is missing')

        vlan_id = helpers.get_user_param('VLAN_ID')
        if not vlan_id:
            raise ValueError('VLAN_ID is missing')

        if not self.generic_deployed_app_resource_model.vm_uuid:
            raise ValueError('VM _UUID is not set on Generic Deployed App')

        if not self.generic_deployed_app_resource_model.cloud_provider:
            raise ValueError('Cloud Provider is not set on Generic Deployed App')

        self.execute_connect_command(vlan_spec_type, self.generic_deployed_app_resource_model, vlan_id)

    def power_off(self):
        """ Executes 'Power Off' on the vCenter for the deployed app its executed on """
        DeployedAppService.execute_command_on_vcenter_resource(
                self.generic_deployed_app_resource_model,
                "Power Off",
                [InputNameValue('COMMAND', 'power_off'),
                 InputNameValue('RESOURCE_FULLNAME', self.resource_context.fullname),
                 InputNameValue('VM_UUID', self.generic_deployed_app_resource_model.vm_uuid)])

    def power_on(self):
        """ Executes 'Power On' on the vCenter for the deployed app its executed on """
        DeployedAppService.execute_command_on_vcenter_resource(
                self.generic_deployed_app_resource_model,
                "Power On",
                [InputNameValue('COMMAND', 'power_on'),
                 InputNameValue('RESOURCE_FULLNAME', self.resource_context.fullname),
                 InputNameValue('VM_UUID', self.generic_deployed_app_resource_model.vm_uuid)])

    def destroy_vm(self):
        """ Executes 'Destroy VM' on the vCenter for the deployed app its executed on """
        DeployedAppService.execute_command_on_vcenter_resource(
                self.generic_deployed_app_resource_model,
                "Destroy VM",
                [InputNameValue('COMMAND', 'destroy_vm'),
                 InputNameValue('RESOURCE_FULLNAME', self.resource_context.fullname),
                 InputNameValue('VM_UUID', self.generic_deployed_app_resource_model.vm_uuid)])

    def refresh_ip(self):
        """ Executes 'Refresh IP' on the vCenter for the deployed app its executed on """
        DeployedAppService.execute_command_on_vcenter_resource(
                self.generic_deployed_app_resource_model,
                "Refresh IP",
                [InputNameValue('COMMAND', 'refresh_ip'),
                 InputNameValue('RESOURCE_FULLNAME', self.resource_context.fullname),
                 InputNameValue('VM_UUID', self.generic_deployed_app_resource_model.vm_uuid)])

    @staticmethod
    def execute_connect_command(access_mode, generic_deployed_app_resource_model, virtual_network):
        DeployedAppService.execute_command_on_vcenter_resource_and_passthrough_result(
                generic_deployed_app_resource_model,
                'Connect VM',
                [InputNameValue('COMMAND', "connect"),
                 InputNameValue('VLAN_ID', virtual_network),
                 InputNameValue('VLAN_SPEC_TYPE', access_mode),
                 InputNameValue('VM_UUID', generic_deployed_app_resource_model.vm_uuid)])

    @staticmethod
    def execute_command_on_vcenter_resource(generic_deployed_app_resource_model, command, inputs):
        session = helpers.get_api_session()
        reservation_id = helpers.get_reservation_context_details().id

        _logger.debug('Executing ' + command + ' command on ' + generic_deployed_app_resource_model.cloud_provider)

        command_result = session.ExecuteCommand(reservation_id,
                                                generic_deployed_app_resource_model.cloud_provider,
                                                'Resource',
                                                command,
                                                inputs,
                                                True)

        _logger.info('Command ' + command + ' result: ' + command_result.Output)

        return command_result

    @staticmethod
    def execute_command_on_vcenter_resource_and_passthrough_result(generic_deployed_app_resource_model, command,
                                                                   inputs):
        command_result = DeployedAppService.execute_command_on_vcenter_resource(generic_deployed_app_resource_model,
                                                                                command,
                                                                                inputs)

        result = get_result_from_command_output(command_result.Output)
        _logger.debug('Transferring result to the caller ' + result)
        set_command_result(result)
