import os
import commands
from commands.commandExecuterService import *


def main():

    cloudshellConnectData = { "user" : "admin", "password" : "admin", "domain" : "Global", "reservationId" : "60d62813-7b0a-40b5-af3c-651d16fc3a43" }

    ces = commandExecuterService(cloudshellConnectData)
    commandToRun = os.environ.get('COMMAND')
    
    # execute the command
    getattr(ces, commandToRun)()
    




if __name__ == "__main__":
    main()

