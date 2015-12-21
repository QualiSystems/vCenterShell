import qualipy.scripts.cloudshell_scripts_helpers as helpers
from pyVmomi import vim

from vCenterShell.commands.BaseCommand import BaseCommand
from vCenterShell.pycommon.pyVmomiService import pyVmomiService
from vCenterShell.commands.NetworkAdaptersRetriever import NetworkAdaptersRetriever


class VirtualSwitchConnectCommand(BaseCommand):
    def __init__(self, py_vmomi_service, cs_retriever_service, logger, network_adapters_retriever):
        self.py_vmomi_service = py_vmomi_service
        self.csRetrieverService = cs_retriever_service
        self.logger = logger
        self.network_adapters_retriever = network_adapters_retriever

    def execute(self):

        resource_att = helpers.get_resource_context_details()
        network_name = resource_att["network_name"]
        network_path = resource_att["network_path"]

        inventory_path_data = self.csRetrieverService.getVCenterInventoryPathAttributeData(resource_att)
        vcenter_resource_name = inventory_path_data["vCenter_resource_name"]
        machine_path = inventory_path_data["vm_folder"]

        connection_details = self.resourceConnectionDetailsRetriever.connection_details(vcenter_resource_name)
        si = self.pvService.connect(connection_details.host, connection_details.user, connection_details.password,
                                    connection_details.port)

        network = self.py_vmomi_service.find_network_by_name(si, network_path, network_name)

        vm = self.py_vmomi_service.find_vm_by_name(si, machine_path, vcenter_resource_name)

        virtual_network_cards = self.network_adapters_retriever.retrieve_virtual_network_cards()

        self.new_virtual_port_group(connection_details.host, v_switch_name, port_group_name, vlad_id)
        pass

    
    """
    Method to create a new virtual port group
    :param host_name: host name to configure
    :param v_switch_name: v_switch to configure
    :param port_group_name: the port group to configure
    :param vlan_id: the vlan Id to set
    """
    def new_virtual_port_group(self, host_name, v_switch_name, port_group_name, vlan_id=0):
        try:
            self.logger.info("creating new port group %s on vswitch %s" % (port_group_name, v_switch_name))
            host = self.content.searchIndex.FindByDnsName(dnsName = host_name, vmSearch = False)

            if host is None:
                self.logger.error("could not find host %s", host_name)
                return

            network_config = host.config.network
            network_system = host.configManager.networkSystem

            spec = self.vim.host.PortGroup.Specification()
            spec.name = port_group_name
            spec.vlanId = vlan_id
            spec.vswitchName = v_switch_name
            spec.policy = self.vim.host.NetworkPolicy()
            network_system.AddPortGroup(spec)

            message = "Port group %s created on %s" % (port_group_name, v_switch_name)
            self.logger.info(message)
            return message

        except Exception as e:
            self.logger.error(e)
            return e.msg
