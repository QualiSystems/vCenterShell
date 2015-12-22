# -*- coding: utf-8 -*-

import qualipy.scripts.cloudshell_scripts_helpers as helpers
from pyVmomi import vim

from vCenterShell.commands.BaseCommand import BaseCommand
from vCenterShell.models.VirtualNicModel import VirtualNicModel
from vCenterShell.pycommon.logger import getLogger

_logger = getLogger("vCenterShell")


class DestroyVirtualSwithCommand(BaseCommand):
    pass
