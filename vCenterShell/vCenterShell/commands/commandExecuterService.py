from pyVim.connect import SmartConnect, Disconnect

from vCenterShell.pycommon.ResourceConnectionDetailsRetriever import ResourceConnectionDetailsRetriever
from vCenterShell.pycommon.pyVmomiService import *
from vCenterShell.commands.deployFromTemplateCommand import *
from vCenterShell.commands.DestroyVirtualMachineCommand import *

class CommandExecuterService(object):
    """ main class that publishes all available commands """

    def __init__(self):
        """
        :param cloudshellConnectData:  dictionary with cloudshell connection data
        """
        self.pyVmomiService = pyVmomiService(SmartConnect, Disconnect)

    def deploy(self):
        csDataRetrieverService = cloudshellDataRetrieverService()
        deployFromTemplateCommand(self.pyVmomiService, csDataRetrieverService, ResourceConnectionDetailsRetriever(csDataRetrieverService)) \
            .execute()

    def destroy(self):        
        DestroyVirtualMachineCommand(self.pyVmomiService) \
            .execute()
        

  



