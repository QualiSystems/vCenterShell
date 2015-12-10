from pyVim.connect import SmartConnect, Disconnect
from pycommon.pyVmomiService import *
from demo import basicFlowDemo

def main():

    cloudshellConnectData = { "user" : "admin", "password" : "admin", "domain" : "Global", "reservationId" : "2bfbaafd-baeb-4ffe-bb4b-be73f62d6469" }
    basicFlowDemo.run(pyVmomiService(SmartConnect, Disconnect), cloudshellConnectData)


if __name__ == "__main__":
    main()

