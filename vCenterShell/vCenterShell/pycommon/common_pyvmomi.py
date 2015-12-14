from pyVmomi import vim
import ssl
import requests
import time

class pyVmomiService:
 
    #region ctor

    def __init__(self,connect,disconnect):
        self.pyvmomi_connect = connect
        self.pyvmomi_disconnect = disconnect
        pass

    #endregion

    #region connect/disconnect methods
       
    def connect(self, address, user, password, port=443):    
        """  
        Connect to vCenter via SSL and return SI object
        
        address:    vCenter address (host / ip address)
        user:       user name for authentication
        password:   password for authentication
        port:       port for the SSL connection. Default = 443
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
        #self.pyvmomi_disconnect(si)
        Disconnect(si)
    
    #endregion

    #region get obj methods
    def find_by_uuid(self, si, path, uuid, isVM=True):     
        """
        Finds vm/host by his uuid in the vCenter or returns "None"

        si:         pyvmomi 'ServiceInstance'
        path:       the path to find the object ('dc' or 'dc/folder' or 'dc/folder/folder/etc...')
        uuid:       the object uuid
        isHost:     if true, search for virtual machines, otherwise search for hosts
        """  
        folder = self.get_folder(si, path);
        searchIndex = si.content.searchIndex
        return searchIndex.FindByUuid(folder, uuid, isVM)

    def find_host_by_name(self, si, path, name):     
        """
        Finds datastore in the vCenter or returns "None"

        si:         pyvmomi 'ServiceInstance'
        path:       the path to find the object ('dc' or 'dc/folder' or 'dc/folder/folder/etc...')
        name:       the datastore name to return
        """  
        return self.find_obj_by_path(si, path, name, 'host');

    def find_datastore_by_name(self, si, path, name):     
        """
        Finds datastore in the vCenter or returns "None"

        si:         pyvmomi 'ServiceInstance'
        path:       the path to find the object ('dc' or 'dc/folder' or 'dc/folder/folder/etc...')
        name:       the datastore name to return
        """  
        return self.find_obj_by_path(si, path, name, 'datastore');

    def find_network_by_name(self, si, path, name):     
        """
        Finds datastore in the vCenter or returns "None"

        si:         pyvmomi 'ServiceInstance'
        path:       the path to find the object ('dc' or 'dc/folder' or 'dc/folder/folder/etc...')
        name:       the datastore name to return
        """  
        return self.find_obj_by_path(si, path, name, 'network');

    def find_vm_by_name(self, si, path, name):
        """
        Finds vm in the vCenter or returns "None"

        si:         pyvmomi 'ServiceInstance'
        path:       the path to find the object ('dc' or 'dc/folder' or 'dc/folder/folder/etc...')
        name:       the vm name to return
        """  
        return self.find_obj_by_path(si, path, name, 'vm');

    def find_obj_by_path(self, si, path, name, typeName):
        """
        Finds object in the vCenter or returns "None"

        si:         pyvmomi 'ServiceInstance'
        path:       the path to find the object ('dc' or 'dc/folder' or 'dc/folder/folder/etc...')
        name:       the object name to return
        typeName:   the name of the type, can be (vm, network, host, datastore)
        """  
        
        typeName = typeName + 'Folder'

        folder = self.get_folder(si, path)
        if folder == None:
            return None

        lookIn = None
        if hasattr(folder, typeName):        
            lookIn = getattr(folder, typeName)
        if hasattr(folder, 'childEntity'):
            lookIn = folder
        searchIndex = si.content.searchIndex
        #searches for the spesific vm in the folder
        return searchIndex.FindChild(lookIn, name)

    def get_folder(self,si, path):
        """
        Finds folder in the vCenter or returns "None"

        si:         pyvmomi 'ServiceInstance'
        path:       the path to find the object ('dc' or 'dc/folder' or 'dc/folder/folder/etc...')
        name:       the folder
        """  
        paths = path.split("/")
        searchIndex = si.content.searchIndex
        subFolder = si.content.rootFolder

        for currPath in paths:
            #checks if the current path is nested as a child
            if hasattr(subFolder, "childEntity"):
                child = searchIndex.FindChild(subFolder, currPath)
            
            if child == None and hasattr(subFolder, "vmFolder"):
                child = searchIndex.FindChild(subFolder.vmFolder, currPath)
            
            if child == None and hasattr(subfolder, 'datastoreFolder'):                
                child = searchIndex.FindChild(subFolder.datastoreFolder, currPath)
            
            if child == None and hasattr(subfolder, 'networkFolder'):      
                child = searchIndex.FindChild(subFolder.networkFolder, currPath)
            
            if child == None and hasattr(subfolder, 'hostFolder'):      
                child = searchIndex.FindChild(subFolder.hostFolder, currPath)
            
            if child == None:
                raise Exception("Path not exist")
            else:
                subFolder = child
                child = None;
        return subFolder

    def get_obj(self, content, vimtype, name):
        """
        Return an object by name for a specific type, if name is None the
        first found object is returned

        content:    pyvmomi content object
        vimtype:    the type of object too search
        name:       the object name to return
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

    #endregion

    #region task handling methods

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

    #endregion

    #region VM methods

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
        """ destroy the given vm  """

        print("The current powerState is: {0}. Attempting to power off {1}".format(vm.runtime.powerState, vm.name))

        task = vm.PowerOffVM_Task()
        self.wait_for_task(task)

        print("{0}".format(task.info.state))
        print("Destroying VM {0}".format(vm.name))

        task = vm.Destroy_Task()
        return self.wait_for_task(task)

    #endregion