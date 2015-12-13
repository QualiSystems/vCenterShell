from pyVmomi import vim
from pyVim.connect import SmartConnect, Disconnect
from pycommon.common_pyvmomi import pyVmomiService
import requests
import json
from vNic import *

requests.packages.urllib3.disable_warnings()

class dvSwitchDataRetriever:

    def __init__(self, pvService):
        self.pvService = pvService

    def RetrieveDvSwitchData(self, host, user, pwd, port, name):
        connection = self.pvService.connect(host, user, pwd, port)

        content = connection.RetrieveContent()
        vmMachine = self.pvService.get_obj(content, [vim.VirtualMachine], name)

        nic = vim.vm.device.VirtualEthernetCard
        nics = [ x for x in vmMachine.config.hardware.device if isinstance(x, nic)]

        vNics = []
        for nic in nics:
            vNics.append( vNic(nic.deviceInfo.summary, nic.macAddress, nic.connectable.connected, nic.connectable.startConnected) )

        return vNics
