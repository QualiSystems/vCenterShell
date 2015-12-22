import qualipy.scripts.cloudshell_scripts_helpers as helpers
from pyVmomi import vim

from models.VirtualNicModel import VirtualNicModel
from vCenterShell.commands.BaseCommand import BaseCommand


class NetworkAdaptersRetrieverCommand(BaseCommand):
    def __init__(self, pv_service, cs_retriever_service, resource_connection_details_retriever):
        self.pvService = pv_service
        self.csRetrieverService = cs_retriever_service
        self.resourceConnectionDetailsRetriever = resource_connection_details_retriever

    def execute(self):
        resource_att = helpers.get_resource_context_details()

        inventory_path_data = self.csRetrieverService.getVCenterInventoryPathAttributeData(resource_att)
        vcenter_resource_name = inventory_path_data.vCenter_resource_name

        connection_details = self.resourceConnectionDetailsRetriever.connection_details(vcenter_resource_name)
        si = self.pvService.connect(connection_details.host, connection_details.user, connection_details.password,
                                    connection_details.port)

        content = si.RetrieveContent()
        vmMachine = self.pvService.get_obj(content, [vim.VirtualMachine], vcenter_resource_name)

        return [VirtualNicModel(x.deviceInfo.summary, x.macAddress, x.connectable.connected, x.connectable.startConnected)
                for x in vmMachine.config.hardware.device
                if isinstance(x, vim.vm.device.VirtualEthernetCard)]

