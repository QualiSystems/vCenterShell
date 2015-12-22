class DeployDataHolder(object):
    def __init__(self, resource_context, connection_details, template_model, datastore_name, vm_cluster_model, power_on):
        """
        :param ResourceContextDetails resource_context:
        :param VCenterConnectionDetails connection_details:
        :param VCenterTemplateModel template_model:
        :param str datastore_name:
        :param VMClusterModel vm_cluster_model:
        :param bool power_on:
        """
        self.resource_context = resource_context
        self.connection_details = connection_details
        self.template_model = template_model
        self.datastore_name = datastore_name
        self.vm_cluster_model = vm_cluster_model
        self.power_on = power_on