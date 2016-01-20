"""
vCenter Shell Starter
runs command defined with 'COMMAND' OS environment variable
"""

import os
import sys
import time
import qualipy.scripts.cloudshell_dev_helpers as dev_helpers

from bootstrap import Bootstrapper
from common.logger.service import LoggingService

INITIAL_LOG_LEVEL = os.environ.get("LOG_LEVEL") or "DEBUG"


def main():
    filename = _get_log_filename()
    LoggingService(INITIAL_LOG_LEVEL, INITIAL_LOG_LEVEL, filename)
    bootstrapper = Bootstrapper()
    ces = bootstrapper.get_command_executer_service()
    command_to_run = os.environ.get('COMMAND')

    # for debug
    if len(sys.argv) > 2 and sys.argv[1] == "debug":
        cloudshellConnectData = {"user": "admin", "password": "admin", "domain": "Global",
                                 "reservationId": "17b9c357-bfe8-46b9-9828-47b3e1cacc4f"}

        attachAndGetResourceContext(cloudshellConnectData)
        command_to_run = sys.argv[2]
        os.environ["resourceContext".upper()] = '{"name":"VCenter Template Request", "address":"Service",' \
                                                ' "model":"VCenter Template Request", "family":"VM Request", ' \
                                                '"description":"", "fullname":"", ' \
                                                '"attributes":{"vCenter Template":"vCenter/QualiSB/Alex/test",' \
                                                '"VM Power State":"True",' \
                                                '"VM Storage":"eric ds cluster", ' \
                                                '"VM Cluster":"QualiSB Cluster/LiverPool"}}'

    # execute the command
    getattr(ces, command_to_run)()


def _get_log_filename():
    return os.path.join(os.path.dirname(__file__), '..\\logs\\', 'vCenterShell_' + time.strftime("%Y%m%d-%H%M%S") + '.log')


# for debug
def attachAndGetResourceContext(cloudshellConnectData):
    dev_helpers.attach_to_cloudshell_as(cloudshellConnectData["user"],
                                        cloudshellConnectData["password"],
                                        cloudshellConnectData["domain"],
                                        cloudshellConnectData["reservationId"])


if __name__ == "__main__":
    main()
