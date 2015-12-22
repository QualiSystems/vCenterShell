import jsonpickle
import qualipy.scripts.cloudshell_scripts_helpers as helpers
import json
from qualipy.api.cloudshell_api import *
from pycommon.common_collection_utils import first_or_default

from models.DeployDataHolder import DeployDataHolder
from pycommon.common_name_utils import generate_unique_name
from vCenterShell.commands.BaseCommand import BaseCommand


class DeployFromTemplateCommand(BaseCommand):
    """ Command to Create a VM from a template """

    def __init__(self, pv_service, cs_retriever_service, resource_connection_details_retriever):
        """
        :param pvService:   pyVmomiService Instance
        """
        self.pv_service = pv_service
        self.cs_retriever_service = cs_retriever_service
        self.resource_connection_details_retriever = resource_connection_details_retriever

    def deploy_from_template(self, data_holder):
        si = None
        try:
            # connect
            si = self.pv_service.connect(data_holder.connection_details.host,
                                         data_holder.connection_details.username,
                                         data_holder.connection_details.password,
                                         data_holder.connection_details.port)

            # generate unique name
            vm_name = generate_unique_name(data_holder.template_model.template_name)

            params = self.pv_service.CloneVmParameters(si=si,
                                                       template_name=data_holder.template_model.template_name,
                                                       vm_name=vm_name,
                                                       vm_folder=data_holder.template_model.vm_folder,
                                                       datastore_name=data_holder.datastore_name,
                                                       cluster_name=data_holder.vm_cluster_model.cluster_name,
                                                       resource_pool=data_holder.vm_cluster_model.resource_pool,
                                                       power_on=data_holder.power_on)

            clone_vm_result = self.pv_service.clone_vm(params)
            if clone_vm_result.error:
                raise ValueError(clone_vm_result.error)

            result = DeployResult(vm_name, clone_vm_result.vm.summary.config.uuid)
        finally:
            # disconnect
            if si:
                self.pv_service.disconnect(si)

        return result

    def get_data_for_deployment(self):
        """ execute the command """
        resource_context = helpers.get_resource_context_details()

        # get vCenter resource name, template name, template folder
        template_model = self.cs_retriever_service.getVCenterTemplateAttributeData(resource_context)
        print "Template: {0}, Folder: {1}, vCenter: {2}".format(template_model.template_name, template_model.vm_folder,
                                                                template_model.vCenter_resource_name)

        # get power state of the cloned VM
        power_on = self.cs_retriever_service.getPowerStateAttributeData(resource_context)
        print "Power On: {0}".format(power_on)

        # get cluster and resource pool
        vm_cluster_model = self.cs_retriever_service.getVMClusterAttributeData(resource_context)
        print "Cluster: {0}, Resource Pool: {1}".format(vm_cluster_model.cluster_name, vm_cluster_model.resource_pool)

        # get datastore
        datastore_name = self.cs_retriever_service.getVMStorageAttributeData(resource_context)
        print "Datastore: {0}".format(datastore_name)

        connection_details = self.resource_connection_details_retriever.connection_details(
            template_model.vCenter_resource_name)
        print "Connecting to: {0}, As: {1}, Pwd: {2}, Port: {3}".format(connection_details.host,
                                                                        connection_details.username,
                                                                        connection_details.password,
                                                                        connection_details.port)

        return DeployDataHolder.create_from_params(resource_context,
                                                   connection_details,
                                                   template_model,
                                                   datastore_name,
                                                   vm_cluster_model,
                                                   power_on)

    def create_resource_for_deployed_vm(self, data_holder, deploy_result):
        reservation_id = helpers.get_reservation_context_details().id
        session = helpers.get_api_session()
        session.CreateResource("Virtual Machine", "Virtual Machine", deploy_result.vm_name, deploy_result.vm_name)
        session.AddResourcesToReservation(reservation_id, [deploy_result.vm_name])
        session.SetAttributesValues(
            [ResourceAttributesUpdateRequest(deploy_result.vm_name,
                                             [AttributeNameValue("vCenter Inventory Path",
                                                                 data_holder.template_model.vCenter_resource_name + "/" + data_holder.template_model.vm_folder),
                                              AttributeNameValue("UUID", deploy_result.uuid),
                                              AttributeNameValue("vCenter Template",
                                                                 data_holder.resource_context.attributes[
                                                                     "vCenter Template"])])])

    def replace_app_resource_with_vm_resource(self, data_holder, deploy_result):
        app_name = data_holder.resource_context.name
        self.create_resource_for_deployed_vm(data_holder, deploy_result)

        reservation_id = helpers.get_reservation_context_details().id
        session = helpers.get_api_session()

        services_position = session.GetReservationServicesPositions(reservation_id)
        app_poistion = first_or_default(services_position.ResourceDiagramLayouts, lambda x: x.ResourceName == app_name)

        session.RemoveServicesFromReservation(reservation_id, app_name)
        session.SetReservationResourcePosition(reservation_id, deploy_result.vm_name, app_poistion.X, app_poistion.Y)

    def execute(self):
        data_holder = self.get_data_for_deployment()
        deploy_result = self.deploy_from_template(data_holder)
        self.create_resource_for_deployed_vm(data_holder, deploy_result)
        # self.replace_app_resource_with_vm_resource(data_holder, deploy_result)

    def get_params_from_env(self):
        param = os.environ.get('DEPLOY_DATA')
        return param

    def deserialize_deploy_params(self):
        param = self.get_params_from_env()
        data = DeployDataHolder(json.loads(param))
        if hasattr(data, 'connection_details') and data.connection_details is not None:
            return data

        connection_details = self.resource_connection_details_retriever.connection_details(
            data.template_model.vCenter_resource_name)

        data.connection_details = connection_details

        return data

    def deploy_execute(self):
        data_holder = self.deserialize_deploy_params()
        deploy_result = self.deploy_from_template(data_holder)
        res = jsonpickle.encode(deploy_result, unpicklable=False)
        print res
        # print str({'vm_name': str(deploy_result.vm_name), 'uuid': str(deploy_result.uuid)})
        # self.create_resource_for_deployed_vm(data_holder, deploy_result)
       

class DeployResult(object):
    def __init__(self, vm_name, uuid):
        self.vm_name = vm_name
        self.uuid = uuid
