import requests
import time
import os

from datetime import datetime
from pyVmomi import vim
from common.logger import getLogger
from common.utilites.io import get_path_and_name

logger = getLogger(__name__)


# configure_loglevel("INFO", "INFO", os.path.join(__file__, os.pardir, os.pardir, os.pardir, 'logs', 'vCenter.log'))

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

    def __init__(self, connect, disconnect, vim_import=None):
        self.pyvmomi_connect = connect
        self.pyvmomi_disconnect = disconnect
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
        except IOError as e:
            # logger.info("I/O error({0}): {1}".format(e.errno, e.strerror))
            import traceback
            logger.warn("Connection Error: ({}):\n{}".format(e, traceback.format_exc()))

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

    def get_folder(self, si, path):
        """
        Finds folder in the vCenter or returns "None"

        :param si:         pyvmomi 'ServiceInstance'
        :param path:       the path to find the object ('dc' or 'dc/folder' or 'dc/folder/folder/etc...')
        """

        search_index = si.content.searchIndex
        sub_folder = si.content.rootFolder

        if path is None or not path:
            return sub_folder
        paths = path.split("/")

        for currPath in paths:
            if currPath is None or not currPath:
                continue

            '#checks if the current path is nested as a child'
            child = None
            if hasattr(sub_folder, self.ChildEntity):
                child = search_index.FindChild(sub_folder, currPath)

            if child is None and hasattr(sub_folder, self.VM):
                child = search_index.FindChild(sub_folder.vmFolder, currPath)

            if child is None and hasattr(sub_folder, self.Datastore):
                child = search_index.FindChild(sub_folder.datastoreFolder, currPath)

            if child is None and hasattr(sub_folder, self.Network):
                child = search_index.FindChild(sub_folder.networkFolder, currPath)

            if child is None and hasattr(sub_folder, self.Host):
                child = search_index.FindChild(sub_folder.hostFolder, currPath)

            if child is None and hasattr(sub_folder, self.Datacenter):
                child = search_index.FindChild(sub_folder.datacenterFolder, currPath)

            if child is None:
                return None
            else:
                sub_folder = child
                child = None

        return sub_folder

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
        container = content.viewManager.CreateContainerView(
                content.rootFolder, vimtype, True)
        for c in container.view:
            if name:
                if c.name == name:
                    obj = c
                    break
            else:
                obj = c
                break

        return obj

    def wait_for_task(self, task):
        """ wait for a vCenter task to finish """
        task_done = False
        while not task_done:
            if task.info.state == 'success':
                logger.info("Task succeeded: " + task.info.state)
                return task.info.result

            if task.info.state == 'error':
                logger.info("error type: %s" % task.info.error.__class__.__name__)
                logger.info("found cause: %s" % task.info.error.faultCause)
                raise Exception(task.info.error.faultCause)
            time.sleep(1)

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
                     power_on=True):
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
            """
            self.si = si
            self.template_name = template_name
            self.vm_name = vm_name
            self.vm_folder = vm_folder
            self.datastore_name = datastore_name
            self.cluster_name = cluster_name
            self.resource_pool = resource_pool
            self.power_on = power_on

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

    def clone_vm(self, clone_params):
        """
        Clone a VM from a template/VM and return the vm oject or throws argument is not valid

        :param clone_params: CloneVmParameters =
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

        managed_object = self.get_folder(clone_params.si, clone_params.vm_folder)
        if isinstance(managed_object, self.vim.Datacenter):
            dest_folder = managed_object.vmFolder
        elif isinstance(managed_object, self.vim.Folder):
            dest_folder = managed_object
        else:
            result.error = 'Failed to find folder: {0}'.format(clone_params.vm_folder)
            return result

        template = self.find_vm_by_name(clone_params.si, clone_params.vm_folder, clone_params.template_name)

        if clone_params.datastore_name is None:
            datastore = template.datastore[0]
        else:
            datastore = self.get_obj(clone_params.si.content, [self.vim.Datastore], clone_params.datastore_name)

        if clone_params.resource_pool:
            resource_pool = self.get_obj(clone_params.si.content, [self.vim.ResourcePool], clone_params.resource_pool)
        else:
            '# if None, get the first one'
            cluster = self.get_obj(clone_params.si.content, [self.vim.ClusterComputeResource],
                                   clone_params.cluster_name)
            resource_pool = cluster.resourcePool

        '# set relo_spec'
        relo_spec = self.vim.vm.RelocateSpec()
        relo_spec.datastore = datastore
        relo_spec.pool = resource_pool

        clone_spec = self.vim.vm.CloneSpec()
        clone_spec.location = relo_spec
        clone_spec.powerOn = clone_params.power_on

        logger.info("cloning VM...")

        task = template.Clone(folder=dest_folder, name=clone_params.vm_name, spec=clone_spec)
        vm = self.wait_for_task(task)
        result.vm = vm
        return result

    def destroy_vm(self, vm):
        """ 
        destroy the given vm  
        :param vm: virutal machine pyvmomi object
        """

        logger.info(
                ("The current powerState is: {0}. Attempting to power off {1}".format(vm.runtime.powerState, vm.name)))

        task = vm.PowerOffVM_Task()
        self.wait_for_task(task)

        logger.info(("{0}".format(task.info.state)))
        logger.info(("Destroying VM {0}".format(vm.name)))

        task = vm.Destroy_Task()
        return self.wait_for_task(task)

    def destroy_vm_by_name(self, si, vm_name, vm_path):
        """ 
        destroy the given vm  
        :param si:      pyvmomi 'ServiceInstance'
        :param vm_name: str name of the vm to destroyed
        :param vm_path: str path to the vm that will be destroyed
        """
        if vm_name is not None:
            vm = self.find_vm_by_name(si, vm_path, vm_name)
            if vm:
                return self.destroy_vm(vm)
        raise ValueError('vm not found')

    def destroy_vm_by_uuid(self, si, vm_uuid, vm_path):
        """
        destroy the given vm
        :param si:      pyvmomi 'ServiceInstance'
        :param vm_uuid: str uuid of the vm to destroyed
        :param vm_path: str path to the vm that will be destroyed
        """
        if vm_uuid is not None:
            vm = self.find_by_uuid(si, vm_uuid, vm_path)
            if vm:
                return self.destroy_vm(vm)
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
            if network_key == network.key:
                return network
        return

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
