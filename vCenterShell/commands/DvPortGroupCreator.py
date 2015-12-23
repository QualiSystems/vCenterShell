import os
from pyVmomi import vim
from pycommon.pyVmomiService import *
from pycommon.SynchronousTaskWaiter import *
from pycommon.logger import getLogger
from pycommon.logger import configure_loglevel

logger = getLogger(__name__)


# configure_loglevel("INFO", "INFO", os.path.join(__file__, os.pardir, os.pardir, os.pardir, 'logs', 'vCenter.log'))

class DvPortGroupCreator(object):
    def __init__(self, pyvmomi_service, synchronous_task_waiter):
        self.pyvmomi_service = pyvmomi_service
        self.synchronous_task_waiter = synchronous_task_waiter
        pass

    def create_dv_port_group(self, dv_port_name, dv_switch_name, dv_switch_path, si, spec):
        dv_switch = self.pyvmomi_service.find_network_by_name(si, dv_switch_path, dv_switch_name)

        dv_pg_spec = vim.dvs.DistributedVirtualPortgroup.ConfigSpec()
        dv_pg_spec.name = dv_port_name
        dv_pg_spec.numPorts = 32
        dv_pg_spec.type = vim.dvs.DistributedVirtualPortgroup.PortgroupType.earlyBinding

        dv_pg_spec.defaultPortConfig = vim.dvs.VmwareDistributedVirtualSwitch.VmwarePortConfigPolicy()
        dv_pg_spec.defaultPortConfig.securityPolicy = vim.dvs.VmwareDistributedVirtualSwitch.SecurityPolicy()

        dv_pg_spec.defaultPortConfig.vlan = spec
        dv_pg_spec.defaultPortConfig.vlan.vlanId = [vim.NumericRange(start=1, end=4094)]
        dv_pg_spec.defaultPortConfig.securityPolicy.allowPromiscuous = vim.BoolPolicy(value=True)
        dv_pg_spec.defaultPortConfig.securityPolicy.forgedTransmits = vim.BoolPolicy(value=True)

        dv_pg_spec.defaultPortConfig.vlan.inherited = False
        dv_pg_spec.defaultPortConfig.securityPolicy.macChanges = vim.BoolPolicy(value=False)
        dv_pg_spec.defaultPortConfig.securityPolicy.inherited = False

        task = dv_switch.AddDVPortgroup_Task([dv_pg_spec])
        logger.info("Successfully created DV Port Group ", dv_port_name)
        port_group = self.synchronous_task_waiter.wait_for_task(task)

        return port_group
