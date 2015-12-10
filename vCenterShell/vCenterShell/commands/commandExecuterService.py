from pyVim.connect import SmartConnect, Disconnect
from pycommon.pyVmomiService import *
from deployFromTemplateCommand import *

class commandExecuterService(object):
    """ main class that publishes all available commands """

    def __init__(self, cloudshellConnectData):
        """
        :param cloudshellConnectData:  dictionary with cloudshell connection data
        """
        self.cloudshellConnectData = cloudshellConnectData
        self.pyVmomiService = pyVmomiService(SmartConnect, Disconnect)

    def deploy(self):        
        deployFromTemplateCommand(self.pyVmomiService, self.cloudshellConnectData) \
            .execute()
        

  



