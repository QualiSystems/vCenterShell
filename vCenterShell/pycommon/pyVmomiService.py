import requests
import time

from datetime import datetime
from pyVmomi import vim


class pyVmomiService:

    #region consts
    ChildEntity = 'childEntity'
    VM = 'vmFolder'
    Network = 'networkFolder'
    Datacenter = 'datacenterFolder'
    Host = 'hostFolder'
    Datastore = 'datastoreFolder'
    Cluster = 'cluster'
    DvSwitch = 'dvSwitch'
    #endregion

    def __init__(self, connect, disconnect):
        self.pyvmomi_connect = connect
        self.pyvmomi_disconnect = disconnect

    def connect(self, address, user, password, port=443):
        """  
        Connect to vCenter via SSL and return SI object
        
        :param address: vCenter address (host / ip address)
        :param user:    user name for authentication
        :param password:password for authentication
        :param port:    port for the SSL connection. Default = 443
        """

        # Disabling urllib3 ssl warnings
        requests.packages.urllib3.disable_warnings()

        # Disabling SSL certificate verification
        import ssl
        if hasattr(ssl, 'SSLContext'):
            context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
            context.verify_mode = ssl.CERT_NONE

        try:
            if context:
                #si = SmartConnect(host=address, user=user, pwd=password, port=port, sslContext=context)
                si = self.pyvmomi_connect(host=address, user=user, pwd=password, port=port, sslContext=context)
            else:
                #si = SmartConnect(host=address, user=user, pwd=password, port=port)
                si = self.pyvmomi_connect(host=address, user=user, pwd=password, port=port)
            return si
        except IOError as e:
            print "I/O error({0}): {1}".format(e.errno, e.strerror)

    def disconnect(self, si):
        """ Disconnect from vCenter """
        self.pyvmomi_disconnect(si)

    def find_dv_switch_by_name(self, si, path, name):
        """
        Finds datacenter in the vCenter or returns "None"

        :param si:         pyvmomi 'ServiceInstance'
        :param path:       the path to find the object ('dc' or 'dc/folder' or 'dc/folder/folder/etc...')
        :param name:       the cluster name to return
        """  
        return self.find_obj_by_path(si, path, name, self.DvSwitch)

    def find_cluster_by_name(self, si, path, name):
        """
        Finds datacenter in the vCenter or returns "None"

        :param si:         pyvmomi 'ServiceInstance'
        :param path:       the path to find the object ('dc' or 'dc/folder' or 'dc/folder/folder/etc...')
        :param name:       the cluster name to return
        """
        return self.find_obj_by_path(si, path, name, self.Cluster)

    def find_datacenter_by_name(self, si, path, name):
        """
        Finds datacenter in the vCenter or returns "None"

        :param si:         pyvmomi 'ServiceInstance'
        :param path:       the path to find the object ('dc' or 'dc/folder' or 'dc/folder/folder/etc...')
        :param name:       the datacenter name to return
        """
        return self.find_obj_by_path(si, path, name, self.Datacenter)

    def find_by_uuid(self, si, path, uuid, is_vm=True):
        """
        Finds vm/host by his uuid in the vCenter or returns "None"

        :param si:         pyvmomi 'ServiceInstance'
        :param path:       the path to find the object ('dc' or 'dc/folder' or 'dc/folder/folder/etc...')
        :param uuid:       the object uuid
        :param is_vm:     if true, search for virtual machines, otherwise search for hosts
        """  
        folder = self.get_folder(si, path)
        search_index = si.content.searchIndex
        return search_index.FindByUuid(folder, uuid, is_vm)

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

        now = datetime.now()

        folder = self.get_folder(si, path)
        if folder is None:
            return None

        look_in = None
        if hasattr(folder, type_name):
            look_in = getattr(folder, type_name)
        if hasattr(folder, self.ChildEntity):
            look_in = folder
        if look_in is None:
            return None

        search_index = si.content.searchIndex
        '#searches for the specific vm in the folder'
        res = search_index.FindChild(look_in, name)

        print 'find_obj_by_path took: %s' % (str(datetime.now() - now))
        return res

    def get_folder(self, si, path):
        """
        Finds folder in the vCenter or returns "None"

        :param si:         pyvmomi 'ServiceInstance'
        :param path:       the path to find the object ('dc' or 'dc/folder' or 'dc/folder/folder/etc...')
        """

        now = datetime.now()

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

            if child is None and hasattr(sub_folder,  self.Network):
                child = search_index.FindChild(sub_folder.networkFolder, currPath)

            if child is None and hasattr(sub_folder,  self.Host):
                child = search_index.FindChild(sub_folder.hostFolder, currPath)

            if child is None and hasattr(sub_folder,  self.Datacenter):
                child = search_index.FindChild(sub_folder.datacenterFolder, currPath)

            if child is None:
                return None
            else:
                sub_folder = child
                child = None

        print 'get_folder took: %s' % (str(datetime.now() - now))
        return sub_folder

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
                print "Task succeeded: " + task.info.state
                return task.info.result

            if task.info.state == 'error':
                print "error type: %s" % task.info.error.__class__.__name__
                print "found cause: %s" % task.info.error.faultCause
                task_done = True
                return None
            time.sleep(1)

    def clone_vm(self, content, si, template, vm_name, datacenter_name, vm_folder, datastore_name, cluster_name, resource_pool, power_on):
        """
        Clone a VM from a template/VM, datacenter_name, vm_folder, datastore_name
        cluster_name, resource_pool, and power_on are all optional.
        """

        # if none git the first one
        datacenter = self.get_obj(content, [vim.Datacenter], datacenter_name)
        print datacenter.name

        if vm_folder:
            destfolder = self.get_obj(content, [vim.Folder], vm_folder)
        else:
            destfolder = datacenter.vmFolder

        print vm_folder

        if datastore_name:
            print datastore_name
            datastore = self.get_obj(content, [vim.Datastore], datastore_name)
        else:
            print "store:" + template.datastore[0].info.name
            datastore = self.get_obj(
                content, [vim.Datastore], template.datastore[0].info.name)

        # if None, get the first one
        cluster = self.get_obj(content, [vim.ClusterComputeResource], cluster_name)

        if resource_pool:
            resource_pool = self.get_obj(content, [vim.ResourcePool], resource_pool)
        else:
            resource_pool = cluster.resourcePool

        # set relospec
        relospec = vim.vm.RelocateSpec()
        relospec.datastore = datastore
        relospec.pool = resource_pool

        clonespec = vim.vm.CloneSpec()
        clonespec.location = relospec
        clonespec.powerOn = power_on

        print "cloning VM..."

        task = template.Clone(folder=destfolder, name=vm_name, spec=clonespec)
        return self.wait_for_task(task)

    def destroy_vm(self, content, si, vm):
        """ 
        destroy the given vm  
        :param vm: virutal machine pyvmomi object
        """

        print("The current powerState is: {0}. Attempting to power off {1}".format(vm.runtime.powerState, vm.name))

        task = vm.PowerOffVM_Task()
        self.wait_for_task(task)

        print("{0}".format(task.info.state))
        print("Destroying VM {0}".format(vm.name))

        task = vm.Destroy_Task()
        return self.wait_for_task(task)

    def destroy_vm_by_name(self, content, si, vm_name):
        """ 
        destroy the given vm  
        :param str vm: virutal machine name to destroy
        """

        vm = self.get_obj(content, [vim.VirtualMachine], vm_name)
        if vm is None:
            raise ValueError("Could find Virtual Machine with name {0}".format(vm_name))

        return self.destroy_vm(content, si, vm)
