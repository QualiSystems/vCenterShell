from common.model_factory import ResourceModelParser
from deployed_app_service.proxy.deployed_app_proxy import DeployedAppService


def main():
    DeployedAppService(ResourceModelParser())\
        .connect()

if __name__ == "__main__":
    main()
