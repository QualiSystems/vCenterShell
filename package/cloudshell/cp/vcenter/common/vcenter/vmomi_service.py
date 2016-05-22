import time
import requests
from pyVmomi import vim
from cloudshell.cp.vcenter.common.utilites.io import get_path_and_name
from cloudshell.cp.vcenter.common.vcenter.vm_location import VMLocation
from cloudshell.cp.vcenter.common.utilites.common_utils import str2bool
from cloudshell.cp.vcenter.common.vcenter.task_waiter import SynchronousTaskWaiter

class pyVmomiService:
    # region consts
    ChildEntity = 'childEntity'
    VM = 'vmFolder'
    Network = 'networkFolder'
    Datacenter = 'datacenterFolder'
    Host = 'hostFolder'
    Datastore = 'datastoreFolder'
    Cluster = 'cluster'

    # endregion

    def __init__(self, connect, disconnect, task_waiter, vim_import=None):
        """
        :param SynchronousTaskWaiter task_waiter:
        :return:
        """
        self.pyvmomi_connect = connect
        self.pyvmomi_disconnect = disconnect
        self.task_waiter = task_waiter
        if vim_import is None:
            from pyVmomi import vim
            self.vim = vim
        else:
            self.vim = vim_import

    def connect(self, address, user, password, port=443):
        """  
        Connect to vCenter via SSL and return SI object
        
        :param address: vCenter address (host / ip address)
        :param user:    user name for authentication
        :param password:password for authentication
        :param port:    port for the SSL connection. Default = 443
        """

        '# Disabling urllib3 ssl warnings'
        requests.packages.urllib3.disable_warnings()

        '# Disabling SSL certificate verification'
        context = None
        import ssl
        if hasattr(ssl, 'SSLContext'):
            context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
            context.verify_mode = ssl.CERT_NONE

        try:
            if context:
                '#si = SmartConnect(host=address, user=user, pwd=password, port=port, sslContext=context)'
                si = self.pyvmomi_connect(host=address, user=user, pwd=password, port=port, sslContext=context)
            else:
                '#si = SmartConnect(host=address, user=user, pwd=password, port=port)'
                si = self.pyvmomi_connect(host=address, user=user, pwd=password, port=port)
            return si
        except vim.fault.InvalidLogin as e:
            raise ValueError(e.msg)
        except IOError as e:
            # logger.info("I/O error({0}): {1}".format(e.errno, e.strerror))
            raise ValueError('Cannot connect to vCenter, please check that the address is valid')

    def disconnect(self, si):
        """ Disconnect from vCenter """
        self.pyvmomi_disconnect(si)

    def find_datacenter_by_name(self, si, path, name):
        """
        Finds datacenter in the vCenter or returns "None"

        :param si:         pyvmomi 'ServiceInstance'
        :param path:       the path to find the object ('dc' or 'dc/folder' or 'dc/folder/folder/etc...')
        :param name:       the datacenter name to return
        """
        return self.find_obj_by_path(si, path, name, self.Datacenter)

    def find_by_uuid(self, si, uuid, is_vm=True, path=None, data_center=None):
        """
        Finds vm/host by his uuid in the vCenter or returns "None"

        :param si:         pyvmomi 'ServiceInstance'
        :param uuid:       the object uuid
        :param path:       the path to find the object ('dc' or 'dc/folder' or 'dc/folder/folder/etc...')
        :param is_vm:     if true, search for virtual machines, otherwise search for hosts
        :param data_center:
        """

        if uuid is None:
            return None
        if path is not None:
            data_center = self.find_item_in_path_by_type(si, path, vim.Datacenter)

        search_index = si.content.searchIndex
        return search_index.FindByUuid(data_center, uuid, is_vm)

    def find_item_in_path_by_type(self, si, path, obj_type):
        """
        This function finds the first item of that type in path
        :param ServiceInstance si: pyvmomi ServiceInstance
        :param str path: the path to search in
        :param type obj_type: the vim type of the object
        :return: pyvmomi type instance object or None
        """
        if obj_type is None:
            return None

        search_index = si.content.searchIndex
        sub_folder = si.content.rootFolder

        if path is None or not path:
            return sub_folder
        paths = path.split("/")

        for currPath in paths:
            if currPath is None or not currPath:
                continue

            manage = search_index.FindChild(sub_folder, currPath)

            if isinstance(manage, obj_type):
                return manage
        return None

    def find_host_by_name(self, si, path, name):
        """
        Finds datastore in the vCenter or returns "None"

        :param si:         pyvmomi 'ServiceInstance'
        :param path:       the path to find the object ('dc' or 'dc/folder' or 'dc/folder/folder/etc...')
        :param name:       the datastore name to return
        """
        return self.find_obj_by_path(si, path, name, self.Host)

    def find_datastore_by_name(self, si, path, name):
        """
        Finds datastore in the vCenter or returns "None"

        :param si:         pyvmomi 'ServiceInstance'
        :param path:       the path to find the object ('dc' or 'dc/folder' or 'dc/folder/folder/etc...')
        :param name:       the datastore name to return
        """
        return self.find_obj_by_path(si, path, name, self.Datastore)

    def find_portgroup(self, si, dv_switch_path, name):
        """
        Returns the portgroup on the dvSwitch
        :param name: str
        :param dv_switch_path: str
        :param si: service instance
        """
        dv_switch = self.get_folder(si, dv_switch_path)
        if dv_switch and dv_switch.portgroup:
            for port in dv_switch.portgroup:
                if port.name == name:
                    return port
        return None

    def find_network_by_name(self, si, path, name):
        """
        Finds network in the vCenter or returns "None"

        :param si:         pyvmomi 'ServiceInstance'
        :param path:       the path to find the object ('dc' or 'dc/folder' or 'dc/folder/folder/etc...')
        :param name:       the datastore name to return
        """
        return self.find_obj_by_path(si, path, name, self.Network)

    def find_vm_by_name(self, si, path, name):
        """
        Finds vm in the vCenter or returns "None"

        :param si:         pyvmomi 'ServiceInstance'
        :param path:       the path to find the object ('dc' or 'dc/folder' or 'dc/folder/folder/etc...')
        :param name:       the vm name to return
        """
        return self.find_obj_by_path(si, path, name, self.VM)

    def find_obj_by_path(self, si, path, name, type_name):
        """
        Finds object in the vCenter or returns "None"

        :param si:         pyvmomi 'ServiceInstance'
        :param path:       the path to find the object ('dc' or 'dc/folder' or 'dc/folder/folder/etc...')
        :param name:       the object name to return
        :param type_name:   the name of the type, can be (vm, network, host, datastore)
        """

        folder = self.get_folder(si, path)
        if folder is None:
            raise KeyError('vmomi managed object not found at: {0}'.format(path))

        look_in = None
        if hasattr(folder, type_name):
            look_in = getattr(folder, type_name)
        if hasattr(folder, self.ChildEntity):
            look_in = folder
        if look_in is None:
            raise KeyError('vmomi managed object not found at: {0}'.format(path))

        search_index = si.content.searchIndex
        '#searches for the specific vm in the folder'
        return search_index.FindChild(look_in, name)

    def get_folder(self, si, path, root=None):
        """
        Finds folder in the vCenter or returns "None"

        :param si:         pyvmomi 'ServiceInstance'
        :param path:       the path to find the object ('dc' or 'dc/folder' or 'dc/folder/folder/etc...')
        """

        search_index = si.content.searchIndex
        sub_folder = root if root else si.content.rootFolder

        if not path:
            return sub_folder

        paths = [p for p in path.split("/") if p]

        child = None
        try:
            new_root = search_index.FindChild(sub_folder, paths[0])
            if new_root:
                child = self.get_folder(si, '/'.join(paths[1:]), new_root)
        except:
            child = None

        if child is None and hasattr(sub_folder, self.ChildEntity):
            new_root = search_index.FindChild(sub_folder, paths[0])
            if new_root:
                child = self.get_folder(si, '/'.join(paths[1:]), new_root)

        if child is None and hasattr(sub_folder, self.VM):
            new_root = search_index.FindChild(sub_folder.vmFolder, paths[0])
            if new_root:
                child = self.get_folder(si, '/'.join(paths[1:]), new_root)

        if child is None and hasattr(sub_folder, self.Datastore):
            new_root = search_index.FindChild(sub_folder.datastoreFolder, paths[0])
            if new_root:
                child = self.get_folder(si, '/'.join(paths[1:]), new_root)

        if child is None and hasattr(sub_folder, self.Network):
            new_root = search_index.FindChild(sub_folder.networkFolder, paths[0])
            if new_root:
                child = self.get_folder(si, '/'.join(paths[1:]), new_root)

        if child is None and hasattr(sub_folder, self.Host):
            new_root = search_index.FindChild(sub_folder.hostFolder, paths[0])
            if new_root:
                child = self.get_folder(si, '/'.join(paths[1:]), new_root)

        if child is None and hasattr(sub_folder, self.Datacenter):
            new_root = search_index.FindChild(sub_folder.datacenterFolder, paths[0])
            if new_root:
                child = self.get_folder(si, '/'.join(paths[1:]), new_root)

        if child is None and hasattr(sub_folder, 'resourcePool'):
            new_root = search_index.FindChild(sub_folder.resourcePool, paths[0])
            if new_root:
                child = self.get_folder(si, '/'.join(paths[1:]), new_root)

        return child

    def get_network_by_full_name(self, si, default_network_full_name):
        """
        Find network by a Full Name
        :param default_network_full_name: <str> Full Network Name - likes 'Root/Folder/Network'
        :return:
        """
        path, name = get_path_and_name(default_network_full_name)
        return self.find_network_by_name(si, path, name) if name else None

    def get_obj(self, content, vimtype, name):
        """
        Return an object by name for a specific type, if name is None the
        first found object is returned

        :param content:    pyvmomi content object
        :param vimtype:    the type of object too search
        :param name:       the object name to return
        """
        obj = None

        container = self._get_all_objects_by_type(content, vimtype)
        for c in container.view:
            if name:
                if c.name == name:
                    obj = c
                    break
            else:
                obj = c
                break

        return obj

    @staticmethod
    def _get_all_objects_by_type(content, vimtype):
        container = content.viewManager.CreateContainerView(
            content.rootFolder, vimtype, True)
        return container

    @staticmethod
    def get_default_from_vcenter_by_type(si, vimtype, accept_multi):
        arr_items = pyVmomiService.get_all_items_in_vcenter(si, vimtype)
        if arr_items:
            if accept_multi or len(arr_items) == 1:
                return arr_items[0]
            raise Exception('There is more the one items of the given type')
        raise KeyError('Could not find item of the given type')

    @staticmethod
    def get_all_items_in_vcenter(si, type_filter, root=None):
        root = root if root else si.content.rootFolder
        container = si.content.viewManager.CreateContainerView(container=root, recursive=True)
        return [item for item in container.view if not type_filter or isinstance(item, type_filter)]

    class CloneVmParameters:
        """
        This is clone_vm method params object
        """

        def __init__(self,
                     si,
                     template_name,
                     vm_name,
                     vm_folder,
                     datastore_name=None,
                     cluster_name=None,
                     resource_pool=None,
                     power_on=True,
                     snapshot=''):
            """
            Constructor of CloneVmParameters
            :param si:              pyvmomi 'ServiceInstance'
            :param template_name:   str: the name of the template/vm to clone
            :param vm_name:         str: the name that will be given to the cloned vm
            :param vm_folder:       str: the path to the location of the template/vm to clone
            :param datastore_name:  str: the name of the datastore
            :param cluster_name:    str: the name of the dcluster
            :param resource_pool:   str: the name of the resource pool
            :param power_on:        bool: turn on the cloned vm
            :param snapshot:        str: the name of the snapshot to clone from
            """
            self.si = si
            self.template_name = template_name
            self.vm_name = vm_name
            self.vm_folder = vm_folder
            self.datastore_name = datastore_name
            self.cluster_name = cluster_name
            self.resource_pool = resource_pool
            self.power_on = str2bool(power_on)
            self.snapshot = snapshot

    class CloneVmResult:
        """
        Clone vm result object, will contain the cloned vm or error message
        """

        def __init__(self, vm=None, error=None):
            """
            Constructor receives the cloned vm or the error message

            :param vm:    cloned vm
            :param error: will contain the error message if there is one
            """
            self.vm = vm
            self.error = error

    def clone_vm(self, clone_params, logger):
        """
        Clone a VM from a template/VM and return the vm oject or throws argument is not valid

        :param clone_params: CloneVmParameters =
        :param logger:
        """
        result = self.CloneVmResult()

        if not isinstance(clone_params.si, self.vim.ServiceInstance):
            result.error = 'si must be init as ServiceInstance'
            return result

        if clone_params.template_name is None:
            result.error = 'template_name param cannot be None'
            return result

        if clone_params.vm_name is None:
            result.error = 'vm_name param cannot be None'
            return result

        if clone_params.vm_folder is None:
            result.error = 'vm_folder param cannot be None'
            return result

        datacenter = self.get_datacenter(clone_params)

        dest_folder = self._get_destination_folder(clone_params)

        vm_location = VMLocation.create_from_full_path(clone_params.template_name)

        template = self._get_template(clone_params, vm_location)

        snapshot = self._get_snapshot(clone_params, template)

        datastore = self._get_datastore(clone_params)

        resource_pool, host = self._get_resource_pool(datacenter.name, clone_params)

        if not resource_pool and not host:
            raise ValueError('The specifed host, cluster or resource pool could not be found')

        '# set relo_spec'
        placement = self.vim.vm.RelocateSpec()
        if resource_pool:
            placement.pool = resource_pool
        if host:
            placement.host = host

        clone_spec = self.vim.vm.CloneSpec()

        if snapshot:
            clone_spec.snapshot = snapshot
            clone_spec.template = False
            placement.diskMoveType = 'createNewChildDiskBacking'
        else:
            placement.datastore = datastore

        # after deployment the vm must be powered off and will be powered on if needed by orchestration driver
        clone_spec.location = placement
        # clone_params.power_on
        # due to hotfix 1 for release 1.0,
        clone_spec.powerOn = False

        logger.info("cloning VM...")
        try:
            task = template.Clone(folder=dest_folder, name=clone_params.vm_name, spec=clone_spec)
            vm = self.task_waiter.wait_for_task(task=task, logger=logger, action_name='Clone VM')

        except vim.fault.NoPermission as error:
            logger.error("vcenter returned - no permission: {0}".format(error))
            raise Exception('Permissions is not set correctly, please check the log for more info.')
        except Exception as e:
            logger.error("error deploying: {0}".format(e))
            raise Exception('Error has occurred while deploying, please look at the log for more info.')

        result.vm = vm
        return result

    def get_datacenter(self, clone_params):
        splited = clone_params.vm_folder.split('/')
        root_path = splited[0]
        datacenter = self.get_folder(clone_params.si, root_path)
        return datacenter

    def _get_destination_folder(self, clone_params):
        managed_object = self.get_folder(clone_params.si, clone_params.vm_folder)
        dest_folder = ''
        if isinstance(managed_object, self.vim.Datacenter):
            dest_folder = managed_object.vmFolder
        elif isinstance(managed_object, self.vim.Folder):
            dest_folder = managed_object
        if not dest_folder:
            raise ValueError('Failed to find folder: {0}'.format(clone_params.vm_folder))
        return dest_folder

    def _get_template(self, clone_params, vm_location):
        template = self.find_vm_by_name(clone_params.si, vm_location.path, vm_location.name)
        if not template:
            raise ValueError('Virtual Machine Template with name {0} was not found under folder {1}'
                             .format(vm_location.name, vm_location.path))
        return template

    def _get_datastore(self, clone_params):
        datastore = ''
        parts = clone_params.datastore_name.split('/')
        if not parts:
            raise ValueError('Datastore could not be empty')
        name = parts[len(parts) - 1]
        if name:
            datastore = self.get_obj(clone_params.si.content,
                                     [self.vim.Datastore],
                                     name)
        if not datastore:
            datastore = self.get_obj(clone_params.si.content,
                                     [self.vim.StoragePod],
                                     name)
            if datastore:
                datastore = sorted(datastore.childEntity,
                                   key=lambda data: data.summary.freeSpace,
                                   reverse=True)[0]

        if not datastore:
            raise ValueError('Could not find Datastore: "{0}"'.format(clone_params.datastore_name))
        return datastore

    def _get_resource_pool(self, datacenter_name, clone_params):

        resource_full_path = '{0}/{1}/{2}'.format(datacenter_name,
                                                  clone_params.cluster_name,
                                                  clone_params.resource_pool)
        obj = self.get_folder(clone_params.si, resource_full_path)

        resource_pool = None
        host = None
        if isinstance(obj, self.vim.HostSystem):
            host = obj
            resource_pool = obj.parent.resourcePool

        elif isinstance(obj, self.vim.ResourcePool):
            resource_pool = obj

        elif isinstance(obj, self.vim.ClusterComputeResource):
            resource_pool = obj.resourcePool

        return resource_pool, host

    def destroy_vm(self, vm, logger):
        """ 
        destroy the given vm  
        :param vm: virutal machine pyvmomi object
        :param logger:
        """

        if vm.runtime.powerState == 'poweredOn':
            logger.info(("The current powerState is: {0}. Attempting to power off {1}"
                         .format(vm.runtime.powerState, vm.name)))
            task = vm.PowerOffVM_Task()
            self.task_waiter.wait_for_task(task=task, logger=logger, action_name="Power Off Before Destroy")

        logger.info(("Destroying VM {0}".format(vm.name)))

        task = vm.Destroy_Task()
        return self.task_waiter.wait_for_task(task=task, logger=logger, action_name="Destroy VM")

    def destroy_vm_by_name(self, si, vm_name, vm_path, logger):
        """ 
        destroy the given vm  
        :param si:      pyvmomi 'ServiceInstance'
        :param vm_name: str name of the vm to destroyed
        :param vm_path: str path to the vm that will be destroyed
        :param logger:
        """
        if vm_name is not None:
            vm = self.find_vm_by_name(si, vm_path, vm_name)
            if vm:
                return self.destroy_vm(vm, logger)
        raise ValueError('vm not found')

    def destroy_vm_by_uuid(self, si, vm_uuid, vm_path, logger):
        """
        destroy the given vm
        :param si:      pyvmomi 'ServiceInstance'
        :param vm_uuid: str uuid of the vm to destroyed
        :param vm_path: str path to the vm that will be destroyed
        :param logger:
        """
        if vm_uuid is not None:
            vm = self.find_by_uuid(si, vm_uuid, vm_path)
            if vm:
                return self.destroy_vm(vm, logger)
        # return 'vm not found'
        # for apply the same Interface as for 'destroy_vm_by_name'
        raise ValueError('vm not found')

    def get_vm_by_uuid(self, si, vm_uuid):
        return self.find_by_uuid(si, vm_uuid, True)

    def get_network_by_name_from_vm(self, vm, network_name):
        for network in vm.network:
            if network_name == network.name:
                return network
        return None

    def get_network_by_key_from_vm(self, vm, network_key):
        for network in vm.network:
            if hasattr(network, 'key') and network_key == network.key:
                return network
        return

    def get_network_by_mac_address(self, vm, mac_address):
        backing = [device.backing for device in vm.config.hardware.device
                   if isinstance(device, vim.vm.device.VirtualEthernetCard)
                   and hasattr(device, 'macAddress')
                   and device.macAddress == mac_address]

        if backing:
            back = backing[0]
            if hasattr(back, 'network'):
                return back.network
            if hasattr(back, 'port'):
                return back.port
        return None

    def get_vnic_by_mac_address(self, vm, mac_address):
        for device in vm.config.hardware.device:
            if isinstance(device, vim.vm.device.VirtualEthernetCard) \
                    and hasattr(device, 'macAddress') and device.macAddress == mac_address:
                # mac address is unique
                return device
        return None

    @staticmethod
    def vm_reconfig_task(vm, device_change):
        """
        Create Task for VM re-configure
        :param vm: <vim.vm obj> VM which will be re-configure
        :param device_change:
        :return: Task
        """
        config_spec = vim.vm.ConfigSpec(deviceChange=device_change)
        task = vm.ReconfigVM_Task(config_spec)
        return task

    @staticmethod
    def vm_get_network_by_name(vm, network_name):
        """
        Try to find Network scanning all attached to VM networks
        :param vm: <vim.vm>
        :param network_name: <str> name of network
        :return: <vim.vm.Network or None>
        """
        # return None
        for network in vm.network:
            if hasattr(network, "name") and network_name == network.name:
                return network
        return None

    @staticmethod
    def _get_snapshot(clone_params, template):
        snapshot_name = getattr(clone_params, 'snapshot', None)
        if not snapshot_name:
            return None

        if not hasattr(template, 'snapshot') and hasattr(template.snapshot, 'rootSnapshotList'):
            raise ValueError('The given vm does not have any snapshots')

        paths = snapshot_name.split('/')
        temp_snap = template.snapshot
        for path in paths:
            if path:
                root = getattr(temp_snap, 'rootSnapshotList', getattr(temp_snap, 'childSnapshotList', None))
                if not root:
                    temp_snap = None
                    break

                temp = pyVmomiService._get_snapshot_from_root_snapshot(path, root)

                if not temp:
                    temp_snap = None
                    break
                else:
                    temp_snap = temp

        if temp_snap:
            return temp_snap.snapshot

        raise ValueError('Could not find snapshot in vm')

    @staticmethod
    def _get_snapshot_from_root_snapshot(name, root_snapshot):
        sorted_by_creation = sorted(root_snapshot, key=lambda x: x.createTime, reverse=True)
        for snapshot_header in sorted_by_creation:
            if snapshot_header.name == name:
                return snapshot_header
        return None
