import os
import sys
import commands
from Bootstrapper import Bootstrapper
from commands.CommandExecuterService import *
import qualipy.scripts.cloudshell_dev_helpers as dev_helpers


def main():

    bootstrapper = Bootstrapper()
    ces = bootstrapper.get_command_executer_service()
    commandToRun = os.environ.get('COMMAND')

    # for debug
    if len(sys.argv) > 2 and sys.argv[1] == "debug":
        cloudshellConnectData = {"user": "admin", "password": "admin", "domain": "Global",
                                 "reservationId": "54636c17-e139-47ba-ac5c-59b6ff6783e7"}
        attachAndGetResourceContext(cloudshellConnectData)
        commandToRun = sys.argv[2]
        os.environ[
            "resourceContext".upper()] = '{"name":"VCenter Template Request", "address":"Service", "model":"VCenter Template Request", "family":"VM Request", "description":"", "fullname":"", "attributes":{"vCenter Template":"vCenter/Alex/test","VM Power State":"True","VM Storage":"eric ds cluster", "VM Cluster":"QualiSB Cluster/LiverPool"}}'

    # execute the command
    getattr(ces, commandToRun)()


# for debug
def attachAndGetResourceContext(cloudshellConnectData):
    dev_helpers.attach_to_cloudshell_as(cloudshellConnectData["user"],
                                        cloudshellConnectData["password"],
                                        cloudshellConnectData["domain"],
                                        cloudshellConnectData["reservationId"])


if __name__ == "__main__":
    main()
