from pyVmomi import vim
import requests
import atexit
from qualipy.api.cloudshell_api import *
import qualipy.scripts.cloudshell_scripts_helpers as helpers
import qualipy.scripts.cloudshell_dev_helpers as dev_helpers
import time
import sys
import pycommon
from pycommon.common_name_utils import generate_unique_name
from pycommon.cloudshellDataRetrieverService import *

class destroyVirtualMachineCommand(object):
    """ Command to Destroy a VM """


    def __init__(self, pvService, cloudshellConnectData):
        """
        :param pvService:              pyVmomiService Instance
        :param cloudshellConnectData:  dictionary with cloudshell connection data
        """
        self.pvService = pvService
        self.cloudshellConnectData = cloudshellConnectData
        self.csRetrieverService = cloudshellDataRetrieverService()


    def execute(self):    
        """ execute the command """
        pass

    def __attachAndGetResourceContext(self):
        dev_helpers.attach_to_cloudshell_as(self.cloudshellConnectData["user"], 
                                            self.cloudshellConnectData["password"], 
                                            self.cloudshellConnectData["domain"], 
                                            self.cloudshellConnectData["reservationId"])
        return helpers.get_resource_context_details()
        
        

  



