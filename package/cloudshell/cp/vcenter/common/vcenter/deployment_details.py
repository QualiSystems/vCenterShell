class DeploymentDetails(object):
    def __init__(self, vm_cluster, vm_storage, vm_resource_pool, vm_location):
        self.vm_cluster = vm_cluster
        self.vm_storage = vm_storage
        self.vm_resource_pool = vm_resource_pool
        self.vm_location = vm_location