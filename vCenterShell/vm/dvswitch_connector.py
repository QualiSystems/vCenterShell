# class VirtualSwitchToMachineConnector(object):
#     def __init__(self, pyvmomi_service, resource_connection_details_retriever, dv_port_group_creator,
#                  virtual_machine_port_group_configurer):
#         self.pyvmomi_service = pyvmomi_service
#         self.resourceConnectionDetailsRetriever = resource_connection_details_retriever
#         self.dv_port_group_creator = dv_port_group_creator
#         self.virtual_machine_port_group_configurer = virtual_machine_port_group_configurer
#
#     def connect(self, virtual_machine_name, dv_switch_path, dv_switch_name, dv_port_name, virtual_machine_path, vm_uuid,
#                 port_group_path, vlad_id, vlan_spec):
#         connection_details = self.resourceConnectionDetailsRetriever.connection_details(virtual_machine_name)
#
#         si = self.pyvmomi_service.connect(connection_details.host, connection_details.username,
#                                           connection_details.password,
#                                           connection_details.port)
#
#         self.dv_port_group_creator.create_dv_port_group(dv_port_name, dv_switch_name, dv_switch_path, si, vlan_spec, vlad_id)
#
#         self.virtual_machine_port_group_configurer.configure_port_group_on_vm(si, virtual_machine_path, vm_uuid,
#                                                                               port_group_path,
#
#                                                                        dv_port_name)



from common.logger import getLogger
logger = getLogger("vCenterShell")

class VirtualSwitchToMachineConnector(object):
    def __init__(self,
                 pyvmomi_service,
                 resource_connection_details_retriever,
                 dv_port_group_creator,
                 virtual_machine_port_group_configurer):
        self.pyvmomi_service = pyvmomi_service
        self.resourceConnectionDetailsRetriever = resource_connection_details_retriever
        self.dv_port_group_creator = dv_port_group_creator
        self.virtual_machine_port_group_configurer = virtual_machine_port_group_configurer


    def connect(self,
                vcenter_name,
                dv_switch_path,
                dv_switch_name,
                dv_port_name,
                #virtual_machine_path,
                vm_uuid,
                port_group_path,
                vlan_id,
                vlan_spec):
        si, vm = self.connect_and_get_vm(vcenter_name, vm_uuid)

        network = self.get_or_create_network(si,
                                             vm,
                                             dv_port_name,
                                             dv_switch_name,
                                             dv_switch_path,
                                             port_group_path,
                                             vlan_id,
                                             vlan_spec)

        self.virtual_machine_port_group_configurer.connect_first_available_vnic(vm, network)

    def connect_specific_vnic(self, vcenter_name, dv_switch_path, dv_switch_name, dv_port_name, vm_uuid, vnic_name,
                              port_group_path, vlan_id, vlan_spec):
        si, vm = self.connect_and_get_vm(vcenter_name, vm_uuid)

        network = self.get_or_create_network(si,
                                             vm,
                                             dv_port_name,
                                             dv_switch_name,
                                             dv_switch_path,
                                             port_group_path,
                                             vlan_id,
                                             vlan_spec)

        self.virtual_machine_port_group_configurer.connect_vinc_port_group(vm, vnic_name, network)

    def connect_networks(self, vcenter_name, vm_uuid, vlan_spec, mapping):
        si, vm = self.connect_and_get_vm(vcenter_name, vm_uuid)
        networks_to_connect = []
        for network_spec in mapping:
            network = self.get_or_create_network(si,
                                                 vm,
                                                 network_spec['dv_port_name'],
                                                 network_spec['dv_switch_name'],
                                                 network_spec['dv_switch_path'],
                                                 network_spec['port_group_path'],
                                                 network_spec['vlan_id'],
                                                 vlan_spec)
            networks_to_connect.append(network)

        self.virtual_machine_port_group_configurer.connect_networks(vm, networks_to_connect)

    def connect_by_mapping(self, vcenter_name, vm_uuid, vlan_spec, mapping):
        si, vm = self.connect_and_get_vm(vcenter_name, vm_uuid)
        vnic_mapping = dict()
        for vnic_name, network_spec in mapping.items():
            network = self.get_or_create_network(si,
                                                 vm,
                                                 network_spec['dv_port_name'],
                                                 network_spec['dv_switch_name'],
                                                 network_spec['dv_switch_path'],
                                                 network_spec['port_group_path'],
                                                 network_spec['vlan_id'],
                                                 vlan_spec)
            vnic_mapping[vnic_name] = network

        self.virtual_machine_port_group_configurer.connect_by_mapping(vm, vnic_mapping)

    def get_or_create_network(self,
                              si,
                              vm,
                              dv_port_name,
                              dv_switch_name,
                              dv_switch_path,
                              port_group_path,
                              vlan_id,
                              vlan_spec):
        # check if the network is attached to the vm and gets it, the function doesn't goes to the vcenter
        network = self.pyvmomi_service.get_network_by_name_from_vm(vm, dv_port_name)

        # if we didn't found the network on the vm
        if network is None:
            # try to get it from the vcenter
            network = self.pyvmomi_service.find_network_by_name(si, port_group_path, dv_port_name)

        # if we still couldn't get the network ---> create it(can't find it, play god!)
        if network is None:
            network = self.dv_port_group_creator.create_dv_port_group(dv_port_name,
                                                                      dv_switch_name,
                                                                      dv_switch_path,
                                                                      si,
                                                                      vlan_spec,
                                                                      vlan_id)
        return network

    def get_si(self, vcenter_name):
        connection_details = self.resourceConnectionDetailsRetriever.connection_details(vcenter_name)
        si = self.pyvmomi_service.connect(connection_details.host,
                                          connection_details.username,
                                          connection_details.password,
                                          connection_details.port)

    def connect_and_get_vm(self, vcenter_name, vm_uuid):
        si = self.get_si(vcenter_name)
        logger.debug("virtual machine vmUUID {}".format(vm_uuid))
        vm = self.pyvmomi_service.find_by_uuid(si, vm_uuid)
        return si, vm
