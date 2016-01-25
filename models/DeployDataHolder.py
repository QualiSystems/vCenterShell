class DeployDataHolder(object):
    def __init__(self, d):
        for a, b in d.items():
            if isinstance(b, dict):
                setattr(self, a, DeployDataHolder(b))
            elif isinstance(b, list):
                items = [self._create_obj_by_type(item) for item in b]
                setattr(self, a, items)
            else:
                setattr(self, a, self._create_obj_by_type(b))

    @staticmethod
    def _create_obj_by_type(obj):
        obj_type = type(obj)
        if obj_type == dict:
            return DeployDataHolder(obj)
        if obj_type == list:
            return [DeployDataHolder._create_obj_by_type(item) for item in obj]
        if DeployDataHolder._is_primitive(obj):
            return obj_type(obj)
        return obj

    @staticmethod
    def _is_primitive(thing):
        primitive = (int, str, bool, float, unicode)
        return isinstance(thing, primitive)

    @classmethod
    def create_from_params(cls, template_model, datastore_name, vm_cluster_model, power_on):
        """
        :param VCenterTemplateModel template_model:
        :param str datastore_name:
        :param VMClusterModel vm_cluster_model:
        :param bool power_on:
        """
        dic = {
            'template_model': template_model,
            'datastore_name': datastore_name,
            'vm_cluster_model': vm_cluster_model,
            'power_on': power_on
        }
        return cls(dic)