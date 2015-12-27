from DeploymentServiceDriver import DeploymentServiceDriver
from pycommon.CloudshellDataRetrieverService import CloudshellDataRetrieverService


def main():
    cs = CloudshellDataRetrieverService()
    dsd = DeploymentServiceDriver(cs)
    dsd.execute()

if __name__ == "__main__":
    main()
