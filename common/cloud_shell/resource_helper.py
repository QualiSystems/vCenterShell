

def get_attribute(attributes, attribute_name, default_value=None):
    attribute = next(item for item in attributes if item.Name == attribute_name)
    if attribute:
        return attribute.Value
    if default_value:
        return default_value
    raise ValueError('Attribute {0} is missing'.format(attribute_name))
