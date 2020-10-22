# util methods to help us work with collections
import urllib.request, urllib.parse, urllib.error
import urllib.parse


def first_or_default(collection, predicate):
    return next(item for item in collection if predicate(item))


# numeric utils
def back_slash_to_front_converter(string):
    """
    Replacing all \ in the str to /
    :param string: single string to modify
    :type string: str
    """
    try:
        if not string or not isinstance(string, str):
            return string
        return string.replace('\\', '/')
    except Exception:
        return string


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
    as_string = ', '.join("%s: %s" % item for item in list(attrs.items()))
    return as_string


def fixurl(url):
    # turn string into unicode
    if not isinstance(url, str):
        url = url.decode('utf8')

    # parse it
    parsed = urllib.parse.urlsplit(url)

    # divide the netloc further
    userpass, at, hostport = parsed.netloc.rpartition('@')
    user, colon1, pass_ = userpass.partition(':')
    host, colon2, port = hostport.partition(':')

    # encode each component
    scheme = parsed.scheme
    user = urllib.parse.quote(user)
    pass_ = urllib.parse.quote(pass_)
    path = '/'.join(  # could be encoded slashes!
        urllib.parse.quote(urllib.parse.unquote(pce), '')
        for pce in parsed.path.split('/')
    )
    query = urllib.parse.quote(urllib.parse.unquote(parsed.query), '=&?/')
    fragment = urllib.parse.quote(urllib.parse.unquote(parsed.fragment))

    # put it back together
    netloc = ''.join((user, colon1, pass_, at, host, colon2, port))
    return urllib.parse.urlunsplit((scheme, netloc, path, query, fragment))


def str2bool(boolean_as_string):
    if isinstance(boolean_as_string, bool):
        return boolean_as_string
    if boolean_as_string.lower() == 'true':
        return True
    if boolean_as_string.lower() == 'false':
        return False
    raise ValueError('{0} should be True or False '.format(boolean_as_string))


def get_error_message_from_exception(ex):
    if hasattr(ex, 'message') and ex.message:
        error_message = ex.message
    elif hasattr(ex, 'msg') and ex.msg:
        error_message = ex.msg
    else:
        error_message = str(ex)

    if hasattr(ex, 'faultMessage'):
        if hasattr(ex.faultMessage, 'message'):
            error_message += '. ' + ex.faultMessage.message

    return error_message
