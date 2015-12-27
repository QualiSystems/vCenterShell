"""
vCenter Shell Starter
"""

import os

from demo import DevBootstrapper
#from vCenterShell.demo.dev_bootstrapper import attachAndGetResourceContext
from pycommon.logging_service import LoggingService


INITIAL_LOG_LEVEL = os.environ.get("LOG_LEVEL") or "DEBUG"
DEFAULT_LOG_FILENAME = "./vCenterTest.log"


def main():
    LoggingService(INITIAL_LOG_LEVEL, INITIAL_LOG_LEVEL, DEFAULT_LOG_FILENAME)
    bootstrapper = DevBootstrapper()
    bootstrapper.connect()
    bootstrapper.disconnect()

    si = bootstrapper.si
    vcenter = bootstrapper.py_vmomi_service

    #boris = vcenter.find_host_by_name(si, "/QualiSB/a/", 'boris1')
    #boris = vcenter.find_host_by_name(si, "/", 'boris1')
    #boris = vcenter.find_vm_by_name(si, "/", 'boris1')
    #boris = vcenter.find_datacenter_by_name(si, "/", 'QualiSB')

    kinds = [   vcenter.ChildEntity,
                vcenter.VM,
                vcenter.Network,
                vcenter.Datacenter,
                vcenter.Host,
                vcenter.Datastore,
                vcenter.Cluster
    ]

    for k in kinds:
        a = vcenter.find_item_in_path_by_type(si, "/d1", k)
        print "{:>20} {}".format(k, a)


    # #attachAndGetResourceContext()
    #
    # command = NetworkAdaptersRetrieverCommand(bootstrapper.py_vmomi_service,
    #                                           bootstrapper.data_retriever_service,
    #                                           bootstrapper.connection_details_retriever)
    # #
    # command.execute()

if __name__ == "__main__":
    main()
