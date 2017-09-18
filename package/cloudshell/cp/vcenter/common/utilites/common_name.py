import uuid

### util methods to help us generate names for different entities ###


def generate_unique_name(name_prefix, reservation_id=None):
    """
    Generate a unique name.
    Method generate a guid and adds the first 8 characteres of the new guid to 'name_prefix'.
    If reservation id is provided than the first 4 chars of the generated guid are taken and the last 4
    of the reservation id
    """
    if reservation_id and isinstance(reservation_id, str) and len(reservation_id) >= 4:
        unique_id = str(uuid.uuid4())[:4] + "-" + reservation_id[-4:]
    else:
        unique_id = str(uuid.uuid4())[:8]
    return name_prefix + "_" + unique_id
