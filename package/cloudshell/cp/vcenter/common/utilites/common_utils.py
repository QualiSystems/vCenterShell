# util methods to help us work with collections
import urllib
import urlparse


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
    as_string = ', '.join("%s: %s" % item for item in attrs.items())
    return as_string


def fixurl(url):
    # turn string into unicode
    if not isinstance(url, unicode):
        url = url.decode('utf8')

    # parse it
    parsed = urlparse.urlsplit(url)

    # divide the netloc further
    userpass, at, hostport = parsed.netloc.rpartition('@')
    user, colon1, pass_ = userpass.partition(':')
    host, colon2, port = hostport.partition(':')

    # encode each component
    scheme = parsed.scheme.encode('utf8')
    user = urllib.quote(user.encode('utf8'))
    colon1 = colon1.encode('utf8')
    pass_ = urllib.quote(pass_.encode('utf8'))
    at = at.encode('utf8')
    host = host.encode('idna')
    colon2 = colon2.encode('utf8')
    port = port.encode('utf8')
    path = '/'.join(  # could be encoded slashes!
        urllib.quote(urllib.unquote(pce).encode('utf8'), '')
        for pce in parsed.path.split('/')
    )
    query = urllib.quote(urllib.unquote(parsed.query).encode('utf8'), '=&?/')
    fragment = urllib.quote(urllib.unquote(parsed.fragment).encode('utf8'))

    # put it back together
    netloc = ''.join((user, colon1, pass_, at, host, colon2, port))
    return urlparse.urlunsplit((scheme, netloc, path, query, fragment))


def str2bool(boolean_as_string):
    if isinstance(boolean_as_string, bool):
        return boolean_as_string
    if boolean_as_string.lower() == 'true':
        return True
    if boolean_as_string.lower() == 'false':
        return False
    raise ValueError('{0} should be True or False '.format(boolean_as_string))


def get_error_message_from_exception(ex):
    error_message = ''  # traceback.format_exc()
    if hasattr(ex, 'message') and ex.message:
        error_message += ex.message
    elif hasattr(ex, 'msg') and ex.msg:
        error_message += ex.msg
    if hasattr(ex, 'faultMessage'):
        if hasattr(ex.faultMessage, 'message'):
            error_message += '. ' + ex.faultMessage.message
    return error_message
