"""
vCenter Shell Starter
"""

import os, sys
import qualipy.scripts.cloudshell_dev_helpers as dev_helpers

from settings import *

from vCenterShell.demo.dev_bootstrapper import DevBootstrapper
from vCenterShell.demo.dev_bootstrapper import attachAndGetResourceContext
from pycommon.logging_service import LoggingService


INITIAL_LOG_LEVEL = os.environ.get("LOG_LEVEL") or "DEBUG"
DEFAULT_LOG_FILENAME = "./vCenterTest.log"


from vCenterShell.commands.NetworkAdaptersRetrieverCommand import NetworkAdaptersRetrieverCommand

def main():
    LoggingService(INITIAL_LOG_LEVEL, INITIAL_LOG_LEVEL, DEFAULT_LOG_FILENAME)
    bootstrapper = DevBootstrapper()

    attachAndGetResourceContext()

    command = NetworkAdaptersRetrieverCommand(bootstrapper.py_vmomi_service,
                                              bootstrapper.data_retriever_service,
                                              bootstrapper.connection_details_retriever)

    command.execute()

if __name__ == "__main__":
    main()
