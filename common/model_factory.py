class ResourceModelParser:
    ATTRIBUTE_NAME_POSTFIX = "_attribute"

    def __init__(self):
        pass

    def convert_to_resource_model(self, resource_instance):
        """
        Converts an instance of resource with dictionary of attributes
        to a class instance according to family and assigns its properties
        :param resource_instance: Instance of resource
        :return:
        """

        instance = ResourceModelParser.create_resource_model_instance(resource_instance)
        props = ResourceModelParser.get_public_properties(instance)
        for attrib in ResourceModelParser.get_resource_attributes(resource_instance):
            property_name = ResourceModelParser.get_property_name_from_attribute_name(attrib)
            property_name_for_attribute_name = ResourceModelParser.get_property_name_with_attribute_name_postfix(attrib)
            if props.__contains__(property_name):
                setattr(instance, property_name, ResourceModelParser.get_resource_attributes(resource_instance)[attrib])
                if hasattr(instance, property_name_for_attribute_name):
                    setattr(instance, property_name_for_attribute_name, attrib)
                    props.remove(property_name_for_attribute_name)
                props.remove(property_name)

        if props:
            raise ValueError('Property(ies) {0} not found on resource with attributes {1}'
                             .format(','.join(props),
                                     ','.join(ResourceModelParser.get_resource_attributes(resource_instance))))
        return instance

    @staticmethod
    def get_resource_attributes(resource_instance):
        if hasattr(resource_instance, "attrib"):
            return resource_instance.attrib
        if hasattr(resource_instance, "ResourceAttributes"):
            return resource_instance.ResourceAttributes
        if hasattr(resource_instance, "attributes"):
            return resource_instance.attributes

    @staticmethod
    def get_public_properties(instance):
        """
        Return list of public properties of an instance
        :param instance: class instance
        :return: list
        """
        return [prop for prop in dir(instance) if not prop.startswith('__')]

    @staticmethod
    def create_resource_model_instance(resource_instance):
        """
        Create an instance of class named *ResourceModel
        from models folder according to ResourceModelName of a resource
        :param resource_instance: Resource with ResourceModelName property
        :return: instance of ResourceModel class
        """
        resource_model = ResourceModelParser.get_resource_model(resource_instance)
        resource_class_name = ResourceModelParser.get_resource_model_class_name(
                resource_model)
        # print 'Family name is ' + resource_class_name
        instance = ResourceModelParser.get_class('models.' + resource_class_name)
        return instance

    @staticmethod
    def get_resource_model(resource_instance):
        if hasattr(resource_instance, "model"):
            return resource_instance.model
        if hasattr(resource_instance, "ResourceModelName"):
            return resource_instance.ResourceModelName

    @staticmethod
    def get_resource_model_class_name(resource_family):
        """
        Returns ResouceModel class name by resource family
        :param resource_family: Resource family
        :rtype: string
        """
        return resource_family.replace(' ', '') + 'ResourceModel'

    @staticmethod
    def get_class(class_path):
        """
        Returns an instance of a class by its class_path.
        :param class_path: contains modules and class name with dot delimited
        :return: Any
        """
        module_path, class_name = class_path.rsplit(".", 1)

        try:
            module = __import__(class_path, fromlist=[class_name])
        except ImportError:
            raise ValueError("Module '%s' could not be imported" % (module_path,))

        try:
            cls = getattr(module, class_name)
        except AttributeError:
            raise ValueError("Module '%s' has no class '%s'" % (module_path, class_name,))

        try:
            instance = cls()
        except TypeError as type_error:
            raise ValueError('Failed to instantiate class {0}. Error: {1}'.format(class_name, type_error.message))

        return instance

    @staticmethod
    def get_property_name_from_attribute_name(attribute_name):
        """
        Returns property name from attribute name
        :param attribute_name: Attribute name, may contain upper and lower case and spaces
        :return: string
        """
        return attribute_name.lower().replace(' ', '_')

    @staticmethod
    def get_property_name_with_attribute_name_postfix(attribute_name):
        """
        Returns property name from attribute name
        :param attribute_name: Attribute name, may contain upper and lower case and spaces
        :return: string
        """
        return ResourceModelParser.get_property_name_from_attribute_name(
            attribute_name) + ResourceModelParser.ATTRIBUTE_NAME_POSTFIX.lower()
