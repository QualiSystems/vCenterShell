from pyVmomi import vim
import ssl
import requests
import time

class pyVmomiService:
 
    #region ctor

    def __init__(self,connect,disconnect):
        self.pyvmomi_connect = connect
        self.pyvmomi_disconnect = disconnect

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
        self.pyvmomi_disconnect(si)
    
    #endregion

    #region get obj methods

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