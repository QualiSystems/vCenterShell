from cloudshell.cp.vcenter.models.VMwarevCenterResourceModel import VMwarevCenterResourceModel
from cloudshell.cp.vcenter.common.utilites.common_utils import back_slash_to_front_converter


class ResourceModelParser:
    ATTRIBUTE_NAME_POSTFIX = "_attribute"

    def __init__(self):
        pass

    def convert_to_vcenter_model(self, resource):
        vcenter_data_model = self.convert_to_resource_model(
            resource_instance=resource,
            resource_model_type=VMwarevCenterResourceModel)

        vcenter_data_model.default_dvswitch = back_slash_to_front_converter(vcenter_data_model.default_dvswitch)
        vcenter_data_model.default_datacenter = back_slash_to_front_converter(vcenter_data_model.default_datacenter)
        vcenter_data_model.reserved_networks = back_slash_to_front_converter(vcenter_data_model.reserved_networks)
        vcenter_data_model.vm_location = back_slash_to_front_converter(vcenter_data_model.vm_location)
        vcenter_data_model.vm_storage = back_slash_to_front_converter(vcenter_data_model.vm_storage)
        vcenter_data_model.vm_resource_pool = back_slash_to_front_converter(vcenter_data_model.vm_resource_pool)
        vcenter_data_model.vm_cluster = back_slash_to_front_converter(vcenter_data_model.vm_cluster)

        return vcenter_data_model

    def convert_to_resource_model(self, resource_instance, resource_model_type):
        """
        Converts an instance of resource with dictionary of attributes
        to a class instance according to family and assigns its properties
        :param resource_instance: Instance of resource
        :param resource_model_type: Resource Model type to create
        :return:
        """
        if resource_model_type:
            if not callable(resource_model_type):
                raise ValueError('resource_model_type {0} cannot be instantiated'.format(resource_model_type))
            instance = resource_model_type()
        else:
            instance = ResourceModelParser.create_resource_model_instance(resource_instance)
        props = ResourceModelParser.get_public_properties(instance)
        for attrib in ResourceModelParser.get_resource_attributes(resource_instance):
            property_name = ResourceModelParser.get_property_name_from_attribute_name(attrib)
            property_name_for_attribute_name = ResourceModelParser.get_property_name_with_attribute_name_postfix(attrib)
            if props.__contains__(property_name):
                value = self.get_attribute_value(attrib, resource_instance)
                setattr(instance, property_name, value)
                if hasattr(instance, property_name_for_attribute_name):
                    setattr(instance, property_name_for_attribute_name, attrib)
                    props.remove(property_name_for_attribute_name)
                props.remove(property_name)

        if props:
            raise ValueError('Property(ies) {0} not found on resource with attributes {1}'
                             .format(','.join(props),
                                     ','.join(ResourceModelParser.get_resource_attributes(resource_instance))))
        return instance

    def get_attribute_value(self, attrib, resource_instance):
        attributes = ResourceModelParser.get_resource_attributes(resource_instance)
        if hasattr(attrib, 'Value') and hasattr(attrib, 'Name'):
            attribute_by_name = [attribute.Value for attribute in attributes if attribute.Name == attrib.Name]
            if attribute_by_name:
                return attribute_by_name[0]
            raise Exception('Attribute {0} not found'.format(attrib.Name))

        return ResourceModelParser.get_resource_attributes(resource_instance)[attrib]

    @staticmethod
    def get_resource_attributes(resource_instance):
        if hasattr(resource_instance, "attrib"):
            return resource_instance.attrib
        if hasattr(resource_instance, "ResourceAttributes"):
            return resource_instance.ResourceAttributes
        if hasattr(resource_instance, "attributes"):
            return resource_instance.attributes
        raise ValueError('Object {0} does not have any attributes property'.format(str(resource_instance)))

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
        instance = ResourceModelParser.get_class('cloudshell.cp.vcenter.models.' + resource_class_name)
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
            raise ValueError('Class {0} could not be imported'.format(class_path))

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
    def get_property_name_from_attribute_name(attribute):
        """
        Returns property name from attribute name
        :param attribute: Attribute name, may contain upper and lower case and spaces
        :return: string
        """
        if isinstance(attribute, str) or isinstance(attribute, unicode):
            attribute_name = attribute
        elif hasattr(attribute, 'Name'):
            attribute_name = attribute.Name
        else:
            raise Exception('Attribute type {0} is not supported'.format(str(type(attribute))))

        return attribute_name.lower().replace(' ', '_')

    @staticmethod
    def get_property_name_with_attribute_name_postfix(attribute):
        """
        Returns property name from attribute name
        :param attribute: Attribute name, may contain upper and lower case and spaces
        :return: string
        """
        return ResourceModelParser.get_property_name_from_attribute_name(attribute) + \
               ResourceModelParser.ATTRIBUTE_NAME_POSTFIX.lower()
