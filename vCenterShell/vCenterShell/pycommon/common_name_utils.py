import uuid

### util methods to help us generate names for different entities ###


def generate_unique_name(name_prefix):
    """
    generate a unique name.
    method generate a guid and adds the first 8 characteres of the new guid to 'name_prefix'.
    """
    unique_id = str(uuid.uuid4())[:8]
    return name_prefix + "_" + unique_id
