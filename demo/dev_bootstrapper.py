from pyVim.connect import SmartConnect, Disconnect

import qualipy.scripts.cloudshell_dev_helpers as dev_helpers

from settings import *

from pycommon.CloudshellDataRetrieverService import CloudshellDataRetrieverService
from pycommon.ResourceConnectionDetailsRetriever import ResourceConnectionDetailsRetriever
from pycommon.pyVmomiService import pyVmomiService


import sys
import os.path
from models.VCenterConnectionDetails import VCenterConnectionDetails
import qualipy.scripts.cloudshell_scripts_helpers as helpers

sys.path.append(os.path.join(os.path.dirname(__file__), '../vCenterShell/vCenterShell'))

from pycommon.logger import getLogger
_logger = getLogger(__name__)

def getConnectDataContext():
    global ConnectData
    return ConnectData


def update_environment():
    os.environ["RESOURCECONTEXT"] = \
            '{' \
            ' "name":"VCenter Template Request", ' \
            ' "address":"Service",' \
            ' "model":"VCenter Template Request", ' \
            ' "family":"VM Request", ' \
            ' "description":"", ' \
            ' "fullname":"", ' \
            ' "attributes":{"vCenter Template":"vCenter/QualiSB/Alex/test",' \
                            '"VM Power State":"True",' \
                            '"VM Storage":"eric ds cluster", ' \
                            '"VM Cluster":"QualiSB Cluster/LiverPool"}}'


class DevBootstrapper(object):
    def __init__(self):
        update_environment()

        self.py_vmomi_service = pyVmomiService(SmartConnect, Disconnect)
        self.data_retriever_service = CloudshellDataRetrieverService()
        self.connection_details_retriever = ResourceConnectionDetailsRetriever(self.data_retriever_service)
        self.si = None

    def connect(self):
        data = getConnectDataContext()
        self.si = self.py_vmomi_service.connect(data["host"],
                                                data["user"],
                                                data["password"],
                                                data["port"])

        _logger.info("CONNECT {}".format("SUCCESS" if self.si else "ERROR"))

    def disconnect(self):
        if self.si:
            self.py_vmomi_service.disconnect(self.si)
            _logger.info("DISCONNECTED")
        else:
            _logger.info("WAS NOT CONNECTED")


# def attachAndGetResourceContext():
#     update_environment()
#     global ConnectData
#     dev_helpers.attach_to_cloudshell_as(ConnectData["user"],
#                                         ConnectData["password"],
#                                         ConnectData["domain"],
#                                         ConnectData["reservationId"])