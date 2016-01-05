# -*- coding: utf-8 -*-

import qualipy.scripts.cloudshell_scripts_helpers as helpers
#
#
# class VirtualSwitchConnectCommand(object):
#     def __init__(self,
#                  cs_retriever_service,
#                  virtual_switch_to_machine_connector,
#                  dv_port_group_name_generator,
#                  vlan_spec_factory,
#                  vlan_id_range_parser,
#                  resourse_model_parser):
#         """
#         :param cs_retriever_service:
#         :param virtual_switch_to_machine_connector:
#         :param dv_port_group_name_generator: DvPortGroupNameGenerator
#         :param vlan_spec_factory: VlanSpecFactory
#         """
#         self.csRetrieverService = cs_retriever_service
#         self.virtual_switch_to_machine_connector = virtual_switch_to_machine_connector
#         self.dv_port_group_name_generator = dv_port_group_name_generator
#         self.vlan_spec_factory = vlan_spec_factory  # type: VlanSpecFactory
#         self.vlan_id_range_parser = vlan_id_range_parser
#         self.resourse_model_parser = resourse_model_parser
#
#     def connect_vm_to_vlan(self, vlan_id, vlan_spec_type):
#         resource_context = helpers.get_resource_context_details()
#         inventory_path_data = self.csRetrieverService.getVCenterInventoryPathAttributeData(resource_context)
#
#         generic_deployed_app_resource_model = self.resourse_model_parser.convert_to_resource_model(resource_context)
#         vm_uuid = generic_deployed_app_resource_model.uuid
#
#         virtual_machine_path = inventory_path_data.vm_folder
#         vcenter_resource_name = inventory_path_data.vCenter_resource_name
#
#         session = helpers.get_api_session()
#         vcenter_resource_details = session.GetResourceDetails(vcenter_resource_name)
#
#         vcenter_resource_model = self.resourse_model_parser.convert_to_resource_model(vcenter_resource_details)
#         dv_switch_path = vcenter_resource_model.default_dvswitch_path
#         dv_switch_name = vcenter_resource_model.default_dvswitch_name
#         port_group_path = vcenter_resource_model.default_port_group_path
#
#         vlan_id_range = self.vlan_id_range_parser.parse_vlan_id(vlan_id)
#         dv_port_name = self.dv_port_group_name_generator.generate_port_group_name(vlan_id)
#         vlan_spec = self.vlan_spec_factory.get_vlan_spec(vlan_spec_type)
#
#         self.virtual_switch_to_machine_connector.connect(vcenter_resource_name, dv_switch_path, dv_switch_name,
#                                                          dv_port_name, virtual_machine_path, vm_uuid,
#                                                          port_group_path, vlan_id_range, vlan_spec)

class VirtualSwitchConnectCommand:
    def __init__(self,
                 cs_retriever_service,
                 virtual_switch_to_machine_connector,
                 dv_port_group_name_generator,
                 vlan_spec_factory,
                 vlan_id_range_parser,
                 resourse_model_parser):
                 #helpers):
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
        self.vlan_id_range_parser = vlan_id_range_parser
        self.resourse_model_parser = resourse_model_parser
        #self.helpers = helpers
        self.resource_context = None
        self.vm_uuid = None
        self.session = None
        self.inventory_path_data = None


    def connect_vm_to_vlan(self, vlan_id, vlan_spec_type):
        resource_context = helpers.get_resource_context_details()
        inventory_path_data = self.csRetrieverService.getVCenterInventoryPathAttributeData(resource_context)

        generic_deployed_app_resource_model = self.resourse_model_parser.convert_to_resource_model(resource_context)
        vm_uuid = generic_deployed_app_resource_model.uuid

        virtual_machine_path = inventory_path_data.vm_folder
        vcenter_resource_name = inventory_path_data.vCenter_resource_name

        session = helpers.get_api_session()
        vcenter_resource_details = session.GetResourceDetails(vcenter_resource_name)

        vcenter_resource_model = self.resourse_model_parser.convert_to_resource_model(vcenter_resource_details)
        dv_switch_path = vcenter_resource_model.default_dvswitch_path
        dv_switch_name = vcenter_resource_model.default_dvswitch_name
        port_group_path = vcenter_resource_model.default_port_group_path

        vlan_id_range = self.vlan_id_range_parser.parse_vlan_id(vlan_id)
        dv_port_name = self.dv_port_group_name_generator.generate_port_group_name(vlan_id)
        vlan_spec = self.vlan_spec_factory.get_vlan_spec(vlan_spec_type)

        self.virtual_switch_to_machine_connector.connect(vcenter_resource_name, dv_switch_path, dv_switch_name,
                                                         dv_port_name, virtual_machine_path, vm_uuid,
                                                         port_group_path, vlan_id_range, vlan_spec)

    def create_context(self, helpers):
        self.resource_context = helpers.get_resource_context_details()
        self.vm_uuid = self.resourse_model_parser.convert_to_resource_model(self.resource_context).uuid
        self.session = helpers.get_api_session()
        self.inventory_path_data = self.csRetrieverService.getVCenterInventoryPathAttributeData(self.resource_context)

    def connect_to_first_vnic(self, vlan_id, vlan_spec_type):
        self.create_context(helpers)
        vcenter_resource_name = self.inventory_path_data.vCenter_resource_name
        vcenter_resource_details = self.session.GetResourceDetails(vcenter_resource_name)

        vcenter_resource_model = self.resourse_model_parser.convert_to_resource_model(vcenter_resource_details)
        dv_switch_path = vcenter_resource_model.default_dvswitch_path
        dv_switch_name = vcenter_resource_model.default_dvswitch_name
        port_group_path = vcenter_resource_model.default_port_group_path

        vlan_id_range = self.vlan_id_range_parser.parse_vlan_id(vlan_id)
        dv_port_name = self.dv_port_group_name_generator.generate_port_group_name(vlan_id)
        vlan_spec = self.vlan_spec_factory.get_vlan_spec(vlan_spec_type)

        self.virtual_switch_to_machine_connector.connect(vcenter_resource_name, dv_switch_path, dv_switch_name,
                                                         dv_port_name, self.vm_uuid, port_group_path, vlan_id_range,
                                                         vlan_spec)

    def connect_specific_vnic(self, vlan_id, vlan_spec_type, vnic_name):
        self.create_context(helpers)
        vcenter_resource_name = self.inventory_path_data.vCenter_resource_name
        vcenter_resource_details = self.session.GetResourceDetails(vcenter_resource_name)

        vcenter_resource_model = self.resourse_model_parser.convert_to_resource_model(vcenter_resource_details)
        dv_switch_path = vcenter_resource_model.default_dvswitch_path
        dv_switch_name = vcenter_resource_model.default_dvswitch_name
        port_group_path = vcenter_resource_model.default_port_group_path

        vlan_id_range = self.vlan_id_range_parser.parse_vlan_id(vlan_id)
        dv_port_name = self.dv_port_group_name_generator.generate_port_group_name(vlan_id)
        vlan_spec = self.vlan_spec_factory.get_vlan_spec(vlan_spec_type)

        self.virtual_switch_to_machine_connector.connect_specific_vnic(vcenter_resource_name, dv_switch_path,
                                                                       dv_switch_name,
                                                                       dv_port_name,
                                                                       self.vm_uuid,
                                                                       vnic_name,
                                                                       port_group_path,
                                                                       vlan_id_range,
                                                                       vlan_spec)

    def connect_networks(self, vlan_id, vlan_spec_type):
        self.create_context(helpers)
        vcenter_resource_name = self.inventory_path_data.vCenter_resource_name
        vcenter_resource_details = self.session.GetResourceDetails(vcenter_resource_name)

        networks_mapping = self.resourse_model_parser.convert_to_resource_model(vcenter_resource_details)
        vlan_spec = self.vlan_spec_factory.get_vlan_spec(vlan_spec_type)

        self.virtual_switch_to_machine_connector.connect_networks(vcenter_resource_name,
                                                                  self.vm_uuid,
                                                                  vlan_spec,
                                                                  networks_mapping)

    def connect_by_mapping(self, vlan_id, vlan_spec_type):
        self.create_context(helpers)
        vcenter_resource_name = self.inventory_path_data.vCenter_resource_name
        vcenter_resource_details = self.session.GetResourceDetails(vcenter_resource_name)

        mapping = self.resourse_model_parser.convert_to_resource_model(vcenter_resource_details)
        vlan_spec = self.vlan_spec_factory.get_vlan_spec(vlan_spec_type)

        self.virtual_switch_to_machine_connector.connect_by_mapping(vcenter_resource_name,
                                                                    self.vm_uuid,
                                                                    vlan_spec,
                                                                    mapping)
