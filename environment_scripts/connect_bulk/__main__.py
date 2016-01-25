from environment_scripts.service.environment import EnvironmentService


def main():
    environment_connector = EnvironmentService()
    environment_connector.connect_bulk()


if __name__ == "__main__":
    main()
