import os
import commands
from commands.commandExecuterService import *
import qualipy.scripts.cloudshell_dev_helpers as dev_helpers

def main():

    # for debug
    #cloudshellConnectData = { "user" : "admin", "password" : "admin", "domain" : "Global", "reservationId" : "60d62813-7b0a-40b5-af3c-651d16fc3a43" }
    #attachAndGetResourceContext(cloudshellConnectData)

    ces = commandExecuterService()
    commandToRun = os.environ.get('COMMAND')
    
    # for debug
    #commandToRun = 'deploy'

    # execute the command
    getattr(ces, commandToRun)()


# for debug
#def attachAndGetResourceContext(cloudshellConnectData):
#    dev_helpers.attach_to_cloudshell_as(cloudshellConnectData["user"], 
#                                        cloudshellConnectData["password"], 
#                                        cloudshellConnectData["domain"], 
#                                        cloudshellConnectData["reservationId"])


if __name__ == "__main__":
    main()

