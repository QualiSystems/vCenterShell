from re import search
import jsonpickle

COMMAND_RESULT_PREFIX = ""
COMMAND_RESULT_POSTFIX = ""
EMPTY_STRING = ""


def get_result_from_command_output(output):
    """
    Extracts result from output
    :param output: Console output as returned from command execution
    :return: Deserialized object or deserialized JSON into dictionary
    """
    if output == EMPTY_STRING or output is None:
        return None
    return jsonpickle.decode(output)


def set_command_result(result, unpicklable=False):
    """
    Serializes output as JSON and writes it to console output wrapped with special prefix and suffix
    :param result: Result to return
    :param unpicklable: If True adds JSON can be deserialized as real object.
                        When False will be deserialized as dictionary
    """
    json = jsonpickle.encode(result, unpicklable=unpicklable)
    result_for_output = COMMAND_RESULT_PREFIX + str(json) + COMMAND_RESULT_POSTFIX
    print result_for_output
    return result_for_output


def transfer_command_result(output):
    print COMMAND_RESULT_PREFIX + output + COMMAND_RESULT_POSTFIX
