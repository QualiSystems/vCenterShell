from vlan_service_scripts.connect.connect_all import ConnectAll
import time

def main():
    time.sleep(30)
    ConnectAll().execute()


if __name__ == "__main__":
    main()
