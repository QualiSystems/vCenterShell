import time

from environment_scripts.setup.setup_script import execute_environment_setup


def main():
    time.sleep(30)
    execute_environment_setup()

if __name__ == "__main__":
    main()
