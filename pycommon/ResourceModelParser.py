class ResourceModelParser:
    def __init__(self):
        pass

    def parse_resource_model(self, resource_instance):
        resource_class_name = self.get_resource_model_class_name(resource_instance.ResourceModelName)
        instance = self.get_class('models.' + resource_class_name)
        for prop in dir(instance):
            if prop in resource_instance.attrib:
                setattr(instance, prop, resource_instance.attrib[prop])
        return instance

    def get_resource_model_class_name(self, resource_model):
        """

        :param resource_model:
        :rtype: string
        """
        return resource_model.replace(' ', '') + 'ResourceModel'

    def get_class(self, class_path):
        module_path, class_name = class_path.rsplit(".", 1)

        try:
            module = __import__(module_path, fromlist=[class_name])
        except ImportError:
            raise ValueError("Module '%s' could not be imported" % (module_path,))

        try:
            cls = getattr(module, class_name)
        except AttributeError:
            raise ValueError("Module '%s' has no class '%s'" % (module_path, class_name,))

        try:
            instance = getattr(cls, class_name)()
        except TypeError as type_error:
            raise ValueError('Failed to instantiate class {0}. Error: {1}'.format(class_name, type_error.message))

        return instance
