from cloudshell.cp.vcenter.common.vcenter.vm_location import VMLocation
from pyVmomi import vim


class VMLoader(object):
    def __init__(self, pv_service):
        """
        :type pv_service: cloudshell.cp.vcenter.common.vcenter.vmomi_service.pyVmomiService
        """
        self.pv_service = pv_service

    def load_vm_uuid_by_name(self, si, vcenter_data_model, vm_name):
        """
        Returns the vm uuid
        :param si: Service instance to the vcenter
        :param vcenter_data_model: vcenter data model
        :param vm_name: the vm name
        :return: str uuid
        """
        path = VMLocation.combine([vcenter_data_model.default_datacenter, vm_name])
        paths = path.split('/')
        name = paths[len(paths) - 1]
        path = VMLocation.combine(paths[:len(paths) - 1])
        vm = self.pv_service.find_vm_by_name(si, path, name)
        if not vm:
            raise ValueError('Could not find the vm in the given path: {0}/{1}'.format(path, name))

        if isinstance(vm, vim.VirtualMachine):
            return vm.config.uuid

        raise ValueError('The given object is not a vm: {0}/{1}'.format(path, name))
