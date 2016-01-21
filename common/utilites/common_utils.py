# util methods to help us work with collections


def first_or_default(collection, predicate):
    return next(item for item in collection if predicate(item))


# numeric utils


def represents_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def get_object_as_string(obj):
    """
    Converts any object to JSON-like readable format, ready to be printed for debugging purposes
    :param obj: Any object
    :return: string
    """
    if isinstance(obj, str):
        return obj
    if isinstance(obj, list):
        return '\r\n\;'.join([get_object_as_string(item) for item in obj])
    attrs = vars(obj)
    as_string = ', '.join("%s: %s" % item for item in attrs.items())
    return as_string
