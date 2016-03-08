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
    def create_from_params(cls, template_model, datastore_name, vm_cluster_model, ip_regex, refresh_ip_timeout,
                           auto_power_on, auto_power_off, wait_for_ip, auto_delete):
        """
        :param VCenterTemplateModel template_model:
        :param str datastore_name:
        :param VMClusterModel vm_cluster_model:
        :param str ip_regex: Custom regex to filter IP addresses
        :param refresh_ip_timeout:
        :param bool auto_power_on:
        :param bool auto_power_off:
        :param bool wait_for_ip:
        :param bool auto_delete:
        """
        dic = {
            'template_model': template_model,
            'datastore_name': datastore_name,
            'vm_cluster_model': vm_cluster_model,
            'ip_regex': ip_regex,
            'refresh_ip_timeout': refresh_ip_timeout,
            'auto_power_on': auto_power_on,
            'auto_power_off': auto_power_off,
            'wait_for_ip': wait_for_ip,
            'auto_delete': auto_delete
        }
        return cls(dic)
