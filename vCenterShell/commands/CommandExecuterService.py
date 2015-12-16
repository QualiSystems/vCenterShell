from pyVim.connect import SmartConnect, Disconnect
from commands.DeployFromTemplateCommand import *
from commands.DestroyVirtualMachineCommand import DestroyVirtualMachineCommand
from pycommon.CloudshellDataRetrieverService import CloudshellDataRetrieverService
from pycommon.ResourceConnectionDetailsRetriever import ResourceConnectionDetailsRetriever
from pycommon.pyVmomiService import *


class CommandExecuterService(object):
    """ main class that publishes all available commands """

    def __init__(self):
        self.pyVmomiService = pyVmomiService(SmartConnect, Disconnect)
        self.cs_data_retriever_service = CloudshellDataRetrieverService()
        self.resource_connection_details_retriever = ResourceConnectionDetailsRetriever(self.cs_data_retriever_service)

    def deploy(self):
        DeployFromTemplateCommand(
                self.pyVmomiService,
                self.cs_data_retriever_service,
                self.resource_connection_details_retriever) \
            .execute()

    def destroy(self):        
        DestroyVirtualMachineCommand(
                self.pyVmomiService,
                self.cs_data_retriever_service,
                self.resource_connection_details_retriever) \
            .execute()
        

  



