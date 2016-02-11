import time

from driver import DeploymentServiceDriver
from common.cloud_shell.data_retriever import CloudshellDataRetrieverService


def main():
    cs = CloudshellDataRetrieverService()
    dsd = DeploymentServiceDriver(cs)
    dsd.execute()

if __name__ == "__main__":
    main()
