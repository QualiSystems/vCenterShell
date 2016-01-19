import qualipy.scripts.cloudshell_scripts_helpers as helpers
from qualipy.api.cloudshell_api import InputNameValue
from common.utilites.command_result import get_result_from_command_output, set_command_result
from common.logger import getLogger

_logger  = getLogger('DeployedAppService')

class DeployedAppService(object):
    def __init__(self, resource_model_parser):
        self.resource_model_parser = resource_model_parser

    def connect(self, access_mode, virtual_network):
        """
        Connect method should be executed on Deployed App
        It executes connect command on vCenter resource for each connected VLAN
        :param virtual_network: virtual network to connect to
        :param access_mode: Access mode: Access or Trunk
        """
        resource_context = helpers.get_resource_context_details()
        generic_deployed_app_resource_model = self.resource_model_parser.convert_to_resource_model(resource_context)

        if not generic_deployed_app_resource_model.vm_uuid:
            raise ValueError('VM _UUID is not set on Generic Deployed App')

        if not generic_deployed_app_resource_model.cloud_provider:
            raise ValueError('Cloud Provider is not set on Generic Deployed App')

        self.execute_command_on_vcenter_resource(access_mode, generic_deployed_app_resource_model, virtual_network)

    @staticmethod
    def execute_command_on_vcenter_resource(access_mode, generic_deployed_app_resource_model, virtual_network):
        session = helpers.get_api_session()
        reservation_id = helpers.get_reservation_context_details().id

        _logger.debug('Executing Connect VM command on ' + generic_deployed_app_resource_model.cloud_provider)

        command_result = session.ExecuteCommand(reservation_id, generic_deployed_app_resource_model.cloud_provider,
                               'Resource',
                               'Connect VM',
                               [InputNameValue('COMMAND', "connect"),
                                InputNameValue('VLAN_ID', virtual_network),
                                InputNameValue('VLAN_SPEC_TYPE', access_mode),
                                InputNameValue('VM_UUID', generic_deployed_app_resource_model.vm_uuid)],
                               True)

        result = get_result_from_command_output(command_result.Output)
        _logger.debug('Transferring result to the caller ' + result)
        set_command_result(result)
