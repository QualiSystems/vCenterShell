from common.model_factory import ResourceModelParser
from driver import DeploymentServiceDriver
from common.cloud_shell.data_retriever import CloudshellDataRetrieverService


def main():
    cs = CloudshellDataRetrieverService()
    resource_model_parser = ResourceModelParser()
    dsd = DeploymentServiceDriver(cs, resource_model_parser)
    dsd.execute()

if __name__ == "__main__":
    main()
