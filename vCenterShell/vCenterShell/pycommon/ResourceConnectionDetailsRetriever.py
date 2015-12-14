import sys
import os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '../vCenterShell/vCenterShell'))
from models.VCenterConnectionDetails import *


class ResourceConnectionDetailsRetriever:

    def __init__(self, cs_retriever_service):
        self.csRetrieverService = cs_retriever_service

    def get_connection_details(self, resource_name):

        reservation_id = helpers.get_reservation_context_details().id
        session = helpers.get_api_session()
        vCenter_details = session.GetResourceDetails(resource_name)
    
        vCenterConn = self.csRetrieverService.getVCenterConnectionDetails(session, vCenter_details)

        return VCenterConnectionDetails(vCenterConn["vCenter_url"], vCenterConn["user"], vCenterConn["password"])
