class DeployDataHolder(object):
    def __init__(self, d):
        for a, b in d.items():
            if isinstance(b, dict):
                setattr(self, a, DeployDataHolder(b))
            elif b is not unicode or b is not str:
                setattr(self, a, b)
            else:
                setattr(self, a, str(b))

    @classmethod
    def create_from_params(cls, resource_context, connection_details, template_model, datastore_name, vm_cluster_model,
                           power_on):
        """
        :param ResourceContextDetails resource_context:
        :param VCenterConnectionDetails connection_details:
        :param VCenterTemplateModel template_model:
        :param str datastore_name:
        :param VMClusterModel vm_cluster_model:
        :param bool power_on:
        """
        dic = {
            'resource_context': resource_context,
            'connection_details': connection_details,
            'template_model': template_model,
            'datastore_name': datastore_name,
            'vm_cluster_model': vm_cluster_model,
            'power_on': power_on
        }
        return cls(dic)