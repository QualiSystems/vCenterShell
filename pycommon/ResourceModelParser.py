class ResourceModelParser:
    def __init__(self):
        pass

    def convert_to_resource_model(self, resource_instance):
        """
        Converts an instance of resource with dictionary of attributes
        to a class instance according to family and assigns its properties
        :param resource_instance: Instance of resource
        :return:
        """
        resource_class_name = self.get_resource_model_class_name(resource_instance.ResourceModelName)
        instance = self.get_class('models.' + resource_class_name)
        for attrib in resource_instance.attrib:
            property_name = ResourceModelParser.get_property_name_from_attribute_name(attrib)
            if hasattr(instance, property_name):
                setattr(instance, property_name, resource_instance.attrib[attrib])

        return instance

    @staticmethod
    def get_resource_model_class_name(resource_model):
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

    @staticmethod
    def get_property_name_from_attribute_name(attribute_name):
        return attribute_name.lower().replace(' ', '_')
