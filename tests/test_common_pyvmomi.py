from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
import unittest
import mock
from mock import Mock, MagicMock, create_autospec, mock_open, patch

import sys
import os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '../vCenterShell/vCenterShell'))

from pycommon.pyVmomiService import pyVmomiService


class test_common_pyvmomi(unittest.TestCase):
    def setUp(self):
        si = create_autospec(spec=vim.ServiceInstance)
        si.RetrieveContent = Mock()
        si.content = create_autospec(spec=vim.ServiceInstanceContent())
        
        mockObj = Mock()
        mockObj.SmartConnect = Mock(return_value=si)
        mockObj.Disconnect = Mock()
        
        self.pvService = pyVmomiService(mockObj.SmartConnect,mockObj.Disconnect)

    def tearDown(self):
        pass

    def test_get_folder_path_not_found(self):
        """
        Checks when path not found
        """
        '#arrange'
        pv_service = pyVmomiService(None, None)

        def find_child_mock(*args):
            root = args[0]
            if hasattr(root, pv_service.ChildEntity):
                for folder in root.childEntity:
                    if folder.name == args[1]:
                        return folder
            else:
                for folder in root:
                    if folder.name == args[1]:
                        return folder
            return None

        si = create_autospec(spec=vim.ServiceInstance)
        si.RetrieveContent = Mock()
        si.content = create_autospec(spec=vim.ServiceInstanceContent())
        si.content.searchIndex = Mock()
        si.content.searchIndex.FindChild = MagicMock(side_effect=find_child_mock)

        first_folder = Mock(spec=[], name='first')
        first_folder.name = 'first'

        second_folder = Mock(spec=[], name='second')
        second_folder.name = 'second'

        third_folder = Mock(spec=[], name='third')
        third_folder.name = 'third'

        fourth_folder = Mock(spec=[], name='fourth')
        fourth_folder.name = 'fourth'

        fifth_folder = Mock(spec=[], name='fifth')
        fifth_folder.name = 'fifth'

        sixth_folder = Mock(spec=[], name='sixth')
        sixth_folder.name = 'sixth'

        si.content.rootFolder = Mock()
        si.content.rootFolder.name = 'rootFolder'
        si.content.rootFolder.childEntity = [first_folder, second_folder]
        first_folder.vmFolder = [second_folder, sixth_folder]
        second_folder.networkFolder = [fourth_folder, third_folder]
        third_folder.hostFolder = [third_folder, fourth_folder]
        fourth_folder.datacenterFolder = [fifth_folder]
        fifth_folder.datastoreFolder = [sixth_folder]

        '#act'
        result = pv_service.get_folder(si, 'first/second/third/first/fifth/sixth')

        '#assert'
        self.assertIsNone(result)

    def test_get_folder_deep_and_complex_path(self):
        """
        Checks when path is deep and complex, goes through all the folder types
        """
        '#arrange'
        pv_service = pyVmomiService(None, None)

        def find_child_mock(*args):
            root = args[0]
            if hasattr(root, pv_service.ChildEntity):
                for folder in root.childEntity:
                    if folder.name == args[1]:
                        return folder
            else:
                for folder in root:
                    if folder.name == args[1]:
                        return folder
            return None

        si = create_autospec(spec=vim.ServiceInstance)
        si.RetrieveContent = Mock()
        si.content = create_autospec(spec=vim.ServiceInstanceContent())
        si.content.searchIndex = Mock()
        si.content.searchIndex.FindChild = MagicMock(side_effect=find_child_mock)

        first_folder = Mock(spec=[], name='first')
        first_folder.name = 'first'

        second_folder = Mock(spec=[], name='second')
        second_folder.name = 'second'

        third_folder = Mock(spec=[], name='third')
        third_folder.name = 'third'

        fourth_folder = Mock(spec=[], name='fourth')
        fourth_folder.name = 'fourth'

        fifth_folder = Mock(spec=[], name='fifth')
        fifth_folder.name = 'fifth'

        sixth_folder = Mock(spec=[], name='sixth')
        sixth_folder.name = 'sixth'

        si.content.rootFolder = Mock()
        si.content.rootFolder.name = 'rootFolder'
        si.content.rootFolder.childEntity = [first_folder, second_folder]
        first_folder.vmFolder = [second_folder, sixth_folder]
        second_folder.networkFolder = [fourth_folder, third_folder]
        third_folder.hostFolder = [third_folder, fourth_folder]
        fourth_folder.datacenterFolder = [fifth_folder]
        fifth_folder.datastoreFolder = [sixth_folder]

        '#act'
        result = pv_service.get_folder(si, 'first/second/third/fourth/fifth/sixth')

        '#assert'
        self.assertEqual(result, sixth_folder)

    def test_get_folder_deep_path(self):
        """
        Checks when path is deep, more then two
        """
        '#arrange'
        pv_service = pyVmomiService(None, None)

        def find_child_mock(*args):
            root = args[0]
            for folder in root.childEntity:
                if folder.name == args[1]:
                    return folder
            return None

        si = create_autospec(spec=vim.ServiceInstance)
        si.RetrieveContent = Mock()
        si.content = create_autospec(spec=vim.ServiceInstanceContent())
        si.content.searchIndex = Mock()
        si.content.searchIndex.FindChild = MagicMock(side_effect=find_child_mock)

        inner_folder = Mock()
        inner_folder.name = 'inner'

        inner_decoy_folder = Mock()
        inner_decoy_folder.name = 'decoy'

        inner_deep_folder = Mock()
        inner_deep_folder.name = 'inner_deep_folder'

        inner_folder.childEntity = [inner_deep_folder, inner_decoy_folder]
        inner_decoy_folder.childEntity = [inner_folder]

        si.content.rootFolder = Mock()
        si.content.rootFolder.childEntity = [inner_decoy_folder, inner_folder]
        si.content.rootFolder.name = 'rootFolder'

        '#act'
        result = pv_service.get_folder(si, 'decoy/inner/inner_deep_folder/')

        '#assert'
        self.assertEqual(result, inner_deep_folder)

    def test_get_folder_one_sub_folder(self):
        """
        Checks when path is only one level deep without '/' and in child entity
        """
        '#arrange'

        pv_service = pyVmomiService(None, None)

        def find_child_mock(*args):
            root = args[0]
            for folder in root.childEntity:
                if folder.name == args[1]:
                    return folder
            return None

        si = create_autospec(spec=vim.ServiceInstance)
        si.RetrieveContent = Mock()
        si.content = create_autospec(spec=vim.ServiceInstanceContent())
        si.content.searchIndex = Mock()
        si.content.searchIndex.FindChild = MagicMock(side_effect=find_child_mock)

        inner_folder = Mock()
        inner_folder.name = 'inner'

        inner_decoy_folder = Mock()
        inner_decoy_folder.name = 'decoy'

        si.content.rootFolder = Mock()
        si.content.rootFolder.childEntity = [inner_decoy_folder, inner_folder]
        si.content.rootFolder.name = 'rootFolder'

        '#act'
        result = pv_service.get_folder(si, 'inner')

        '#assert'
        self.assertEqual(result, inner_folder)

    def test_get_folder_path_empty(self):
        """
        Checks if the receiving path is empty, the function returns root folder
        """
        '#arrange'
        folder_name = 'rootFolder'

        pv_service = pyVmomiService(None, None)

        si = create_autospec(spec=vim.ServiceInstance)
        si.RetrieveContent = Mock()
        si.content = create_autospec(spec=vim.ServiceInstanceContent())

        si.content.rootFolder = Mock()
        si.content.rootFolder.name = folder_name

        '#act'
        result = pv_service.get_folder(si, '')

        '#assert'
        self.assertEqual(result.name, folder_name)

    def test_get_object_by_path_checks_networkFolder(self):
        """
        Checks whether the function can grab network folder
        """
        '#arrange'
        pv_service = pyVmomiService(None, None)

        def search_child(*args, **keys):
            if args[0].name == pv_service.Network:
                return True
            return False

        class FolderMock:
            networkFolder = None

        folder = Mock(spec=FolderMock())
        folder.name = 'parentFolder'
        folder.networkFolder.name = pv_service.Network
        get_folder = MagicMock(return_value=folder)
        pv_service.get_folder = get_folder

        si = create_autospec(spec=vim.ServiceInstance)
        si.RetrieveContent = Mock()
        si.content = create_autospec(spec=vim.ServiceInstanceContent())
        si.content.searchIndex = Mock()
        si.content.searchIndex.FindChild = MagicMock(side_effect=search_child)

        '#act'
        result = pv_service.find_obj_by_path(si, '', '', pv_service.Network)

        '#assert'
        self.assertTrue(result)

    def test_get_object_by_path_checks_hostFolder(self):
        """
        Checks whether the function can grab host folder
        """
        '#arrange'
        pv_service = pyVmomiService(None, None)

        def search_child(*args, **keys):
            if args[0].name == pv_service.Host:
                return True
            return False

        class FolderMock:
            hostFolder = None

        folder = Mock(spec=FolderMock())
        folder.name = 'parentFolder'
        folder.hostFolder.name = pv_service.Host
        get_folder = MagicMock(return_value=folder)
        pv_service.get_folder = get_folder

        si = create_autospec(spec=vim.ServiceInstance)
        si.RetrieveContent = Mock()
        si.content = create_autospec(spec=vim.ServiceInstanceContent())
        si.content.searchIndex = Mock()
        si.content.searchIndex.FindChild = MagicMock(side_effect=search_child)

        '#act'
        result = pv_service.find_obj_by_path(si, '', '', pv_service.Host)

        '#assert'
        self.assertTrue(result)

    def test_get_object_by_path_checks_datacenterFolder(self):
        """
        Checks whether the function can grab datacenter folder
        """
        '#arrange'
        pv_service = pyVmomiService(None, None)

        def search_child(*args, **keys):
            if args[0].name == pv_service.Datacenter:
                return True
            return False

        class FolderMock:
            datacenterFolder = None

        folder = Mock(spec=FolderMock())
        folder.name = 'parentFolder'
        folder.datacenterFolder.name = pv_service.Datacenter
        get_folder = MagicMock(return_value=folder)
        pv_service.get_folder = get_folder

        si = create_autospec(spec=vim.ServiceInstance)
        si.RetrieveContent = Mock()
        si.content = create_autospec(spec=vim.ServiceInstanceContent())
        si.content.searchIndex = Mock()
        si.content.searchIndex.FindChild = MagicMock(side_effect=search_child)

        '#act'
        result = pv_service.find_obj_by_path(si, '', '', pv_service.Datacenter)

        '#assert'
        self.assertTrue(result)

    def test_get_object_by_path_checks_datastoreFolder(self):
        """
        Checks whether the function can grab datastore folder
        """
        '#arrange'
        pv_service = pyVmomiService(None, None)

        def search_child(*args, **keys):
            if args[0].name == pv_service.Datastore:
                return True
            return False

        class FolderMock:
            datastoreFolder = None

        folder = Mock(spec=FolderMock())
        folder.name = 'parentFolder'
        folder.datastoreFolder.name = pv_service.Datastore
        get_folder = MagicMock(return_value=folder)
        pv_service.get_folder = get_folder

        si = create_autospec(spec=vim.ServiceInstance)
        si.RetrieveContent = Mock()
        si.content = create_autospec(spec=vim.ServiceInstanceContent())
        si.content.searchIndex = Mock()
        si.content.searchIndex.FindChild = MagicMock(side_effect=search_child)

        '#act'
        result = pv_service.find_obj_by_path(si, '', '', pv_service.Datastore)

        '#assert'
        self.assertTrue(result)

    def test_get_object_by_path_checks_vmFolder(self):
        """
        Checks whether the function can grab vm folder
        """
        '#arrange'
        pv_service = pyVmomiService(None, None)

        def search_child(*args, **keys):
            if args[0].name == pv_service.VM:
                return True
            return False

        class FolderMock:
            vmFolder = None

        folder = Mock(spec=FolderMock())
        folder.name = 'parentFolder'
        folder.vmFolder.name = pv_service.VM
        get_folder = MagicMock(return_value=folder)
        pv_service.get_folder = get_folder

        si = create_autospec(spec=vim.ServiceInstance)
        si.RetrieveContent = Mock()
        si.content = create_autospec(spec=vim.ServiceInstanceContent())
        si.content.searchIndex = Mock()
        si.content.searchIndex.FindChild = MagicMock(side_effect=search_child)

        '#act'
        result = pv_service.find_obj_by_path(si, '', '', pv_service.VM)

        '#assert'
        self.assertTrue(result)

    def test_get_object_by_path_checks_childEntity(self):
        """
        Checks whether the function can grab from child entities
        """
        '#arrange'
        pv_service = pyVmomiService(None, None)

        def search_child(*args, **keys):
            if args[0].name == pv_service.ChildEntity:
                return True
            return False

        class FolderMock:
            childEntity = None

        folder = Mock(spec=FolderMock())
        folder.name = pv_service.ChildEntity
        get_folder = MagicMock(return_value=folder)
        pv_service.get_folder = get_folder

        si = create_autospec(spec=vim.ServiceInstance)
        si.RetrieveContent = Mock()
        si.content = create_autospec(spec=vim.ServiceInstanceContent())
        si.content.searchIndex = Mock()
        si.content.searchIndex.FindChild = MagicMock(side_effect=search_child)

        '#act'
        result = pv_service.find_obj_by_path(si, '', '', '')

        '#assert'
        self.assertTrue(result)

    def test_get_object_by_path_no_nested_objs(self):
        """
        Checks whether the function returns 'None' if it doesn't find an object
        """
        '#arrange'
        pv_service = pyVmomiService(None, None)

        get_folder = MagicMock(return_value=Mock(spec=[]))
        pv_service.get_folder = get_folder

        si = create_autospec(spec=vim.ServiceInstance)
        si.RetrieveContent = Mock()
        si.content = create_autospec(spec=vim.ServiceInstanceContent())

        '#act'
        result = pv_service.find_obj_by_path(si, '', '', '')

        '#assert'
        self.assertIsNone(result)

    def test_get_vm_by_uuid_vm_in_folder(self):
        """
        Checks whether the function can grab object by uuid
        """
        '#arrange'
        pv_service = pyVmomiService(None, None)

        def find_by_uuid_mock(*args, **kwargs):
            folder = args[0]['vmFolder_test']
            uuid = args[1]
            isVM = args[2]
            if not isVM:
                return False

            for item in folder:
                if item == uuid: return True
            return False

        get_folder = MagicMock(return_value={
            'vmFolder_test': [
                'b8e4d6de-a2ff-11e5-bf7f-feff819cdc9f',
                'b8e4da4e-a2ff-11e5-bf7f-feff819cdc9f']})
        pv_service.get_folder = get_folder

        si = create_autospec(spec=vim.ServiceInstance)
        si.RetrieveContent = Mock()
        si.content = create_autospec(spec=vim.ServiceInstanceContent())

        si.content.searchIndex = Mock()
        si.content.searchIndex.FindByUuid = Mock(side_effect=find_by_uuid_mock)

        '#act'
        result = pv_service.find_by_uuid(si, '', 'b8e4da4e-a2ff-11e5-bf7f-feff819cdc9f')

        '#assert'
        self.assertTrue(result)

    def test_get_vm_by_name_isVm_VM_type(self):
        """
        Checks whether the function can passes vm type
        """
        '#arrange'
        pv_service = pyVmomiService(None, None)

        def find_obj_by_path_mock(*args, **kwargs):
            return args[3] == pv_service.VM

        si = create_autospec(spec=vim.ServiceInstance)
        si.RetrieveContent = Mock()
        si.content = create_autospec(spec=vim.ServiceInstanceContent())

        pv_service.find_obj_by_path = Mock(side_effect=find_obj_by_path_mock)

        '#act'
        result = pv_service.find_vm_by_name(si, '', '')

        '#assert'
        self.assertTrue(result)

    def test_get_datastore_by_name_is_Datastore_type(self):
        """
        Checks whether the function can passes datastore type
        """
        '#arrange'
        pv_service = pyVmomiService(None, None)

        def find_obj_by_path_mock(*args, **kwargs):
            return args[3] == pv_service.Datastore

        si = create_autospec(spec=vim.ServiceInstance)
        si.RetrieveContent = Mock()
        si.content = create_autospec(spec=vim.ServiceInstanceContent())

        pv_service.find_obj_by_path = Mock(side_effect=find_obj_by_path_mock)

        '#act'
        result = pv_service.find_datastore_by_name(si, '', '')

        '#assert'
        self.assertTrue(result)

    def test_get_datacenter_by_name_is_Datacenter_type(self):
        """
        Checks whether the function can passes datascenter type
        """
        '#arrange'
        pv_service = pyVmomiService(None, None)

        def find_obj_by_path_mock(*args, **kwargs):
            return args[3] == pv_service.Datacenter

        si = create_autospec(spec=vim.ServiceInstance)
        si.RetrieveContent = Mock()
        si.content = create_autospec(spec=vim.ServiceInstanceContent())

        pv_service.find_obj_by_path = Mock(side_effect=find_obj_by_path_mock)

        '#act'
        result = pv_service.find_datacenter_by_name(si, '', '')

        '#assert'
        self.assertTrue(result)

    def test_get_host_by_name_is_Host_type(self):
        """
        Checks whether the function can passes host type
        """
        '#arrange'
        pv_service = pyVmomiService(None, None)
        def find_obj_by_path_mock(*args, **kwargs):
            return args[3] == pv_service.Host

        si = create_autospec(spec=vim.ServiceInstance)
        si.RetrieveContent = Mock()
        si.content = create_autospec(spec=vim.ServiceInstanceContent())

        pv_service.find_obj_by_path = Mock(side_effect=find_obj_by_path_mock)

        '#act'
        result = pv_service.find_host_by_name(si, '', '')

        '#assert'
        self.assertTrue(result)

    def test_get_network_by_name_is_network_type(self):
        """
        Checks whether the function can passes network type
        """
        '#arrange'
        pv_service = pyVmomiService(None, None)
        def find_obj_by_path_mock(*args, **kwargs):
            return args[3] == pv_service.Network

        si = create_autospec(spec=vim.ServiceInstance)
        si.RetrieveContent = Mock()
        si.content = create_autospec(spec=vim.ServiceInstanceContent())

        pv_service.find_obj_by_path = Mock(side_effect=find_obj_by_path_mock)

        '#act'
        result = pv_service.find_network_by_name(si, '', '')

        '#assert'
        self.assertTrue(result)




    #def test_can_connect_successfully(self):
    #    #arrange
    #    si = self.pvService.connect("vCenter", "user", "pass")
    #    #assert
    #    result = "1"
    #    self.assertEqual(result,"1")