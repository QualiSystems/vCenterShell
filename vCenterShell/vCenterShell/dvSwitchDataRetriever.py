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
        si = self.pvService.connect(host, user, pwd, port)

        content = si.RetrieveContent()
        vmMachine = self.pvService.get_obj(content, [vim.VirtualMachine], name)

        return [ vNic(x.deviceInfo.summary, x.macAddress, x.connectable.connected, x.connectable.startConnected) \
                for x in vmMachine.config.hardware.device \
                if isinstance(x, vim.vm.device.VirtualEthernetCard)]
