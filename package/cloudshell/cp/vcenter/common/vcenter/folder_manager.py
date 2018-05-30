from threading import Lock
from cloudshell.cp.vcenter.common.vcenter.vm_location import VMLocation


class FolderManager(object):
    def __init__(self, pv_service, si):
        self.saved_apps_folder_lock = Lock()
        self.saved_sandbox_folder_lock = Lock()
        self.pv_service = pv_service
        self.si = si

    def get_or_create_vcenter_folder(self, path, folder_name):
        folder_parent = self.pv_service.get_folder(self.si, path)
        if not folder_parent:
            raise Exception("Could not find " + path)

        vcenter_folder_path = VMLocation.combine([path, folder_name])
        vcenter_folder = self.pv_service.get_folder(self.si, vcenter_folder_path)
        if not vcenter_folder:
            folder_parent.CreateFolder(folder_name)

    def prepare_cloned_vm_vcenter_folder_structure(self, data_holder, saved_sandbox_id, vcenter_data_model):
        vm_location_path = VMLocation.combine([vcenter_data_model.default_datacenter,
                                               data_holder.template_resource_model.vm_location])

        saved_apps_folder = self.get_or_create_saved_apps_folder_in_vcenter(vm_location_path)
        self.get_or_create_saved_sandbox_folder(saved_apps_folder, saved_sandbox_id, data_holder)

    def get_or_create_saved_sandbox_folder(self, saved_apps_folder, saved_sandbox_id, data_holder):
        sandbox_path = self._vcenter_sandbox_folder_path(saved_sandbox_id, data_holder)
        saved_sandbox_folder = self.pv_service.get_folder(self.si, sandbox_path)
        if not saved_sandbox_folder:
            saved_apps_folder.CreateFolder(saved_sandbox_id)

    def get_or_create_saved_apps_folder_in_vcenter(self, vm_location_path):
        saved_apps_path = VMLocation.combine([vm_location_path, "SavedApps"])

        saved_apps_folder = self.pv_service.get_folder(self.si, saved_apps_path)
        if not saved_apps_folder:
            with self.saved_apps_folder_lock:
                saved_apps_folder = self.pv_service.get_folder(self.si, saved_apps_path)
                if not saved_apps_folder:
                    vm_location_folder = self.pv_service.get_folder(self.si, vm_location_path)
                    saved_apps_folder = vm_location_folder.CreateFolder("SavedApps")
        return saved_apps_folder

    def _vcenter_sandbox_folder_path(self, saved_sandbox_id, data_holder):
        return '/'.join([data_holder.template_resource_model.vm_location,
                         'SavedApps',
                         saved_sandbox_id])

    def update_cloned_vm_target_location(self, data_holder, saved_sandbox_id):
        data_holder.template_resource_model.vm_location = self._vcenter_sandbox_folder_path(saved_sandbox_id,
                                                                                            data_holder)
