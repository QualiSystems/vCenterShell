from models.VCenterConnectionDetails import VCenterConnectionDetails
from models.VCenterTemplateModel import *
from models.VCenterInventoryPathAttribute import VCenterInventoryPathAttribute
from models.VMClusterModel import *
from pycommon.common_collection_utils import first_or_default


class CloudshellDataRetrieverService:
    PATH_DELIMITER = "/"

    def getVCenterTemplateAttributeData(self, resource_attributes):
        """ get vCenter resource name, template name, template folder from 'vCenter Template' attribute """

        template_att = resource_attributes.attributes["vCenter Template"]
        template_components = template_att.split(self.PATH_DELIMITER)

        return VCenterTemplateModel(
                vCenter_resource_name=template_components[0],
                vm_folder=self.PATH_DELIMITER.join(template_components[1:-1]),
                template_name=template_components[-1])

    def getPowerStateAttributeData(self, resource_attributes):
        """
        get power state attribute data 
        :rtype: boolean
        """
        power_state = False
        if resource_attributes.attributes["VM Power State"].lower() == "true":
            power_state = True
        return power_state

    def getVMClusterAttributeData(self, resource_attributes):
        """ 
        get cluster and resource pool from 'VM Cluster' attribute 
        if attribute is empty than return None as values
        :rtype VMClusterModel:
        """
        result = VMClusterModel(None, None)

        storage_att = resource_attributes.attributes["VM Cluster"]
        if storage_att:
            storage_att_components = storage_att.split("/")
            if len(storage_att_components) == 2:
                result.cluster_name = storage_att_components[0]
                result.resource_pool = storage_att_components[1]

        return result

    def getVMStorageAttributeData(self, resource_attributes):
        """ get datastore from 'VM Storage' attribute """
        datastore_name = resource_attributes.attributes["VM Storage"]
        if not datastore_name:
            datastore_name = None
        return datastore_name

    def getVCenterConnectionDetails(self, session, vCenter_resource_details):
        """
        Return a dictionary with vCenter connection details. Methods receives a ResourceDetails object of a vCenter resource
        and retrieves the connection details from its attributes.

        :param vCenter_resource_details:   the ResourceDetails object of a vCenter resource
        :param session:                    the cloushell api session, its needed in order to decrypt the password
        """
        user = first_or_default(vCenter_resource_details.ResourceAttributes, lambda att: att.Name == "User").Value
        encryptedPass = first_or_default(vCenter_resource_details.ResourceAttributes,
                                         lambda att: att.Name == "Password").Value
        vcenter_url = vCenter_resource_details.Address
        password = session.DecryptPassword(encryptedPass).Value

        return VCenterConnectionDetails(vcenter_url, user, password)

    def getVCenterInventoryPathAttributeData(self, resource_attributes):
        """ get vCenter resource name & virtual machine folder path """

        path_att = resource_attributes.attributes["vCenter Inventory Path"]
        path_components = path_att.split("/")

        vm_folder = ""
        if (len(path_components) > 1):
            vm_folder = "/".join(path_components[1:])

        return VCenterInventoryPathAttribute(
            vCenter_resource_name=path_components[0],
            vm_folder=vm_folder
        )
