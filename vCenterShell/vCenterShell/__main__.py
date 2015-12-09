from pyVim.connect import SmartConnect, Disconnect
from pycommon.common_pyvmomi import \pyVmomiService
from demo import basicFlowDemo

def main():

    basicFlowDemo.run(pyVmomiService(SmartConnect, Disconnect), "2bfbaafd-baeb-4ffe-bb4b-be73f62d6469")
    #basicFlowDemo.run(pyVmomiService(None, None), "2bfbaafd-baeb-4ffe-bb4b-be73f62d6469")


if __name__ == "__main__":
    main()

