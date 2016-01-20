from re import search

COMMAND_RESULT_PREFIX = "command_json_result="
COMMAND_RESULT_POSTFIX = "=command_json_result_end"

def get_result_from_command_output(output):

    match = search(COMMAND_RESULT_PREFIX + '(?P<result>.*)' + COMMAND_RESULT_POSTFIX, output)
    if not match:
        return output
    return match.group('result')

def set_command_result(output):
    print COMMAND_RESULT_PREFIX + str(output) + COMMAND_RESULT_POSTFIX