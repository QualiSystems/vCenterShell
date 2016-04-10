from re import search
import jsonpickle

COMMAND_RESULT_PREFIX = ""
COMMAND_RESULT_POSTFIX = ""

# COMMAND_RESULT_PREFIX = "command_json_result="
# COMMAND_RESULT_POSTFIX = "=command_json_result_end"


def get_result_from_command_output(output):
    """
    Extracts result from output
    :param output: Console output as returned from command execution
    :return: Deserialized object or deserialized JSON into dictionary
    """
    match = _extract_result_from_output(output)
    if not match:
        return None
    json = match.group('result')
    return jsonpickle.decode(json)


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
    match = _extract_result_from_output(output)
    if match:
        print COMMAND_RESULT_PREFIX + match.group('result') + COMMAND_RESULT_POSTFIX


def _extract_result_from_output(output):
    match = search(COMMAND_RESULT_PREFIX + '(?P<result>.*)' + COMMAND_RESULT_POSTFIX, output)
    return match
