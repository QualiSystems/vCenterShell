import time
import jsonpickle
from cloudshell.api.cloudshell_api import InputNameValue
from common.cloud_shell.data_retriever import CloudshellDataRetrieverService
from common.cloud_shell.driver_helper import CloudshellDriverHelper
from models.DeployDataHolder import DeployDataHolder


class DeployFromImage(object):
    def __init__(self):
        self.cs_helper = CloudshellDriverHelper()
        self.cs_data_retriever = CloudshellDataRetrieverService()

    def initialize(self, context):
        pass

    def Deploy(self, context, Name=None):
        """
        Deploys app from image
        :type context: models.QualiDriverModels.ResourceCommandContext
        """
        session = self.cs_helper.get_session(context.connectivity.server_address,
                                             context.connectivity.admin_auth_token,
                                             context.reservation.domain)

        # get vCenter resource name, template name, template folder
        image_model = self.cs_data_retriever.get_vcenter_image_attribute_data(context.resource.attributes)
        vcenter_res = image_model.vcenter_name

        deployment_info = self._get_deployment_info(image_model, Name)
        result = session.ExecuteCommand(context.reservation.reservation_id,
                                        vcenter_res,
                                        "Resource",
                                        "deploy_from_image",
                                        self._get_command_inputs_list(deployment_info),
                                        False)
        return result.Output

    def _get_deployment_info(self, image_model, name):
        """
        :type image_model: models.vCenterVMFromImageResourceModel.VCenterImageModel
        """
        # todo: raz a after refactoring of the attributes remove this and use "VM Datacenter"
        data_cluster_path = image_model.vm_cluster.split('/')

        cluster = data_cluster_path[1]
        datacenter = data_cluster_path[0]


        return DeployDataHolder({
            "vcenter_name": image_model.vcenter_name,
            "vm_folder": image_model.vm_location,
            "power_on": image_model.auto_power_on,
            "app_name": name,
            "cluster_name": cluster,  # todo: raz a after refactoring of the attributes remove this and use "VM Cluster"
            "resource_pool": image_model.vm_resource_pool,
            "datastore_name": image_model.vm_storage,
            "datacenter_name": datacenter,  # todo: raz a after refactoring of the attributes remove this and use "VM Datacenter"
            "image_url": image_model.vcenter_image})

    def _get_command_inputs_list(self, data_holder):
        return [InputNameValue('deploy_data', jsonpickle.encode(data_holder, unpicklable=False))]
