from pyVim.connect import SmartConnect, Disconnect
from pycommon.pyVmomiService import *
from vCenterShell.commands.deployFromTemplateCommand import *
from vCenterShell.commands.destroyVirtualMachineCommand import *

class commandExecuterService(object):
    """ main class that publishes all available commands """

    def __init__(self):
        """
        :param cloudshellConnectData:  dictionary with cloudshell connection data
        """
        self.pyVmomiService = pyVmomiService(SmartConnect, Disconnect)

    def deploy(self):        
        deployFromTemplateCommand(self.pyVmomiService, CloudshellDataRetrieverService()) \
            .execute()

    def destroy(self):        
        destroyVirtualMachineCommand(self.pyVmomiService) \
            .execute()
        

  



