from environment_scripts import EnvironmentService


def main():
    environment_connector = EnvironmentService()
    environment_connector.connect_all()


if __name__ == "__main__":
    main()
