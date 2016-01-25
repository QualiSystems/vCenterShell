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
        ret_obj = obj
        if isinstance(obj, dict):
            ret_obj = DeployDataHolder(obj)
        if isinstance(obj, str):
            ret_obj = str(obj)
        if isinstance(obj, unicode):
            ret_obj = unicode(obj)
        if isinstance(obj, int):
            ret_obj = int(obj)
        if isinstance(obj, float):
            ret_obj = float(obj)
        return ret_obj


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