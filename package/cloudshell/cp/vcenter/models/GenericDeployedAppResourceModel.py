class GenericDeployedAppResourceModel(object):
    def __init__(self):
        self.vm_uuid = ''
        self.cloud_provider = ''
        self.cloud_provider_attributes = []
        self.fullname = ''
        self.vm_custom_params = None

    def get_reserved_networks(self):
        return self.cloud_provider_attributes['Reserved Networks'].split(';')

    def get_refresh_ip_regex(self):
        return self._get_custom_param('ip_regex')

    def get_refresh_ip_timeout(self):
        return self._get_custom_param('refresh_ip_timeout')

    def _get_custom_param(self, custom_param_name):
        return next((p.value for p in (self.vm_custom_params or []) if p.name == custom_param_name), None)