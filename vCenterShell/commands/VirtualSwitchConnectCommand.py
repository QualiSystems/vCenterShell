import qualipy.scripts.cloudshell_scripts_helpers as helpers

from pycommon.common_collection_utils import first_or_default


class VirtualSwitchConnectCommand:
    def __init__(self, cs_retriever_service, virtual_switch_to_machine_connector,
                 dv_port_group_name_generator, vlan_spec_factory):
        """
        :param cs_retriever_service:
        :param virtual_switch_to_machine_connector:
        :param dv_port_group_name_generator: DvPortGroupNameGenerator
        :param vlan_spec_factory: VlanSpecFactory
        """
        self.csRetrieverService = cs_retriever_service
        self.virtual_switch_to_machine_connector = virtual_switch_to_machine_connector
        self.dv_port_group_name_generator = dv_port_group_name_generator
        self.vlan_spec_factory = vlan_spec_factory  # type: VlanSpecFactory

    def connect_vm_to_vlan(self, vlan_id, vlan_spec_type):
        resource_context = helpers.get_resource_context_details()
        inventory_path_data = self.csRetrieverService.getVCenterInventoryPathAttributeData(resource_context)

        vm_uuid = resource_context.attributes['UUID']

        virtual_machine_path = inventory_path_data.vm_folder
        vcenter_resource_name = inventory_path_data.vCenter_resource_name

        session = helpers.get_api_session()
        vcenter_resource_details = session.GetResourceDetails(vcenter_resource_name)

        dv_switch_path = first_or_default(vcenter_resource_details.ResourceAttributes,
                                          lambda att: att.Name == 'Default dvSwitch Path').Value
        dv_switch_name = first_or_default(vcenter_resource_details.ResourceAttributes,
                                          lambda att: att.Name == 'Default dvSwitch Name').Value
        port_group_path = first_or_default(vcenter_resource_details.ResourceAttributes,
                                           lambda att: att.Name == 'Default port group path').Value

        dv_port_name = self.dv_port_group_name_generator.generate_port_group_name(vlan_id)
        vlan_spec = self.vlan_spec_factory.get_vlan_spec(vlan_spec_type)

        self.virtual_switch_to_machine_connector.connect(vcenter_resource_name, dv_switch_path, dv_switch_name,
                                                         dv_port_name, virtual_machine_path, vm_uuid,
                                                         port_group_path, vlan_id, vlan_spec)
