from pyVmomi import vim
import uuid
from vCenterShell.pycommon.pyVmomiService import *


class VirtualSwitchToMachineConnector(object):
    def __init__(self, pyvmomi_service, synchronous_task_witer, resource_connection_details_retriever):
        self.pyvmomi_service = pyvmomi_service
        self.SynchronousTaskWaiter = synchronous_task_witer
        self.resourceConnectionDetailsRetriever = resource_connection_details_retriever

    def connect(self, vlan_id, virtual_machine_name, virtual_machine_path, network_name, network_path,
                datacenter_name, cluster_path, cluster_name):

        connection_details = self.resourceConnectionDetailsRetriever.connection_details(virtual_machine_name)
        si = self.pyvmomi_service.connect(connection_details.host, connection_details.username,
                                          connection_details.password,
                                          connection_details.port)

        datacenter = self.pyvmomi_service.find_datacenter_by_name(si, '', datacenter_name)
        # cluster = self.pyvmomi_service.find_cluster_by_name(si, cluster_path, cluster_name)
        cluster = self.pyvmomi_service.get_obj(si.RetrieveContent(), [vim.ClusterComputeResource], cluster_name)

        dvs_name = "VLAN " + str(uuid.uuid4())
        return self.create_dv_switch(si, datacenter.networkFolder, cluster, dvs_name)

    def create_dv_switch(self, si, network_folder, cluster, dvs_name):
        pnic_specs = []
        dvs_host_configs = []
        uplink_port_names = []
        dvs_create_spec = vim.DistributedVirtualSwitch.CreateSpec()
        dvs_config_spec = vim.DistributedVirtualSwitch.ConfigSpec()
        dvs_config_spec.name = dvs_name
        dvs_config_spec.uplinkPortPolicy = vim.DistributedVirtualSwitch.NameArrayUplinkPortPolicy()
        hosts = cluster.host
        for x in range(len(hosts)):
            uplink_port_names.append("dvUplink%d" % x)

        for host in hosts:
            dvs_config_spec.uplinkPortPolicy.uplinkPortName = uplink_port_names
            dvs_config_spec.maxPorts = 2000
            pnic_spec = vim.dvs.HostMember.PnicSpec()
            pnic_spec.pnicDevice = 'vmnic1'
            pnic_specs.append(pnic_spec)
            dvs_host_config = vim.dvs.HostMember.ConfigSpec()
            dvs_host_config.operation = vim.ConfigSpecOperation.add
            dvs_host_config.host = host
            dvs_host_configs.append(dvs_host_config)
            dvs_host_config.backing = vim.dvs.HostMember.PnicBacking()
            dvs_host_config.backing.pnicSpec = pnic_specs
            dvs_config_spec.host = dvs_host_configs

        dvs_create_spec.configSpec = dvs_config_spec
        dvs_create_spec.productInfo = vim.dvs.ProductSpec(version='5.1.0')

        task = network_folder.CreateDVS_Task(dvs_create_spec)
        self.SynchronousTaskWaiter.wait_for_task(task, si)
        print "Successfully created DVS ", dvs_name
        return self.pyvmomi_service.find_dv_switch_by_name(si, network_folder, dvs_name)
