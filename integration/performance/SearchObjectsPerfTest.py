import ConfigParser
import os
from unittest import TestCase

from vCenterShell.common.logger import getLogger
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim

from PerfMethodWrapper import PerfMethodWrapper
from tests.utils.testing_credentials import TestCredentials
from vCenterShell.common.vcenter.vmomi_service import pyVmomiService

# consts
START = 'START'
END = 'END'
PERFORMANCE_TEST = '[Performance_Testing] [{0}] {1}'
config = ConfigParser.ConfigParser()
config_path = os.path.join(os.path.dirname(__file__), 'config.ini')
config.readfp(open(config_path))
N_RUNS = int(config.get('performance', 'n_runs'))


class SearchObjectsPerfTest(TestCase):
    def __init__(self, method_ame='runTest'):
        super(SearchObjectsPerfTest, self).__init__(method_ame)
        cred = TestCredentials()
        self.pv_service = pyVmomiService(SmartConnect, Disconnect)
        self.si = self.pv_service.connect(cred.host, cred.username, cred.password)
        self.logger = getLogger('performance')

    # def test_get_object_get_flat_object(self):
    #     def action():
    #         return self.pv_service.get_obj(self.si.content, [vim.VirtualMachine], 'DC0_C0_RP10_VM24')
    #
    #     self.logger.info(PERFORMANCE_TEST.format('test_get_object_get_flat_object', START))
    #     runner = PerfMethodWrapper(action,
    #                                'test_get_object_get_flat_object',
    #                                self.logger)
    #     runner.run(N_RUNS)
    #     self.logger.info(PERFORMANCE_TEST.format('test_get_object_get_flat_object', END))
    #
    # def test_get_object_get_nested_object(self):
    #     def action():
    #         # vm name = DC0_C0_RP0_VM0
    #         return self.pv_service.get_obj(self.si.content, [vim.VirtualMachine], 'DC0_C0_RP0_VM0')
    #
    #     self.logger.info(PERFORMANCE_TEST.format('get_object_get_nested_object', START))
    #     runner = PerfMethodWrapper(action,
    #                                'get_object_get_nested_object',
    #                                self.logger)
    #     runner.run(N_RUNS)
    #     self.logger.info(PERFORMANCE_TEST.format('get_object_get_nested_object', END))

    def test_find_by_name_nested_object(self):
        def action():
            # vm name = DC0_C0_RP0_VM0
            return self.pv_service.find_vm_by_name(self.si, 'DC0/raz_test/raztest2/final', 'DC0_C0_RP0_VM0')

        self.logger.info(PERFORMANCE_TEST.format('test_find_by_name_nested_object', START))
        runner = PerfMethodWrapper(action,
                                   'test_find_by_name_nested_object',
                                   self.logger)
        runner.run(N_RUNS)
        self.logger.info(PERFORMANCE_TEST.format('test_find_by_name_nested_object', END))

    def test_find_by_uuid_flat_obj_with_dc_object(self):
        dc = self.pv_service.find_item_in_path_by_type(self.si, 'DC0', vim.Datacenter)

        def action():
            # vm name = DC0_C0_RP0_VM0
            return self.pv_service.find_by_uuid(self.si, '423634ae-0188-ff08-a60a-83f1b43a2cc4', True, None, dc)

        self.logger.info(PERFORMANCE_TEST.format('test_find_by_uuid_flat_obj_with_dc_object', START))
        runner = PerfMethodWrapper(action,
                                   'test_find_by_uuid_flat_obj_with_dc_object',
                                   self.logger)
        runner.run(N_RUNS)
        self.logger.info(PERFORMANCE_TEST.format('test_find_by_uuid_flat_obj_with_dc_object', END))

    def test_find_by_uuid_with_dc_object(self):
        dc = self.pv_service.find_item_in_path_by_type(self.si, 'DC0', vim.Datacenter)

        def action():
            # vm name = DC0_C0_RP0_VM0
            return self.pv_service.find_by_uuid(self.si, '4236d4e4-f36a-9bf5-1d61-7c31e9059cfc', True, None, dc)

        self.logger.info(PERFORMANCE_TEST.format('test_find_by_uuid_with_dc_object', START))
        runner = PerfMethodWrapper(action,
                                   'test_find_by_uuid_with_dc_object',
                                   self.logger)
        runner.run(N_RUNS)
        self.logger.info(PERFORMANCE_TEST.format('test_find_by_uuid_with_dc_object', END))

    def test_find_by_uuid_with_dc_path(self):
        def action():
            # vm name = DC0_C0_RP0_VM0
            return self.pv_service.find_by_uuid(self.si, '4236d4e4-f36a-9bf5-1d61-7c31e9059cfc', True, 'DC0')

        self.logger.info(PERFORMANCE_TEST.format('test_find_by_uuid_with_dc_path', START))
        runner = PerfMethodWrapper(action,
                                   'test_find_by_uuid_with_dc_path',
                                   self.logger)
        runner.run(N_RUNS)
        self.logger.info(PERFORMANCE_TEST.format('test_find_by_uuid_with_dc_path', END))

    def test_find_by_uuid_without_path_nested_object(self):
        def action():
            # vm name = DC0_C0_RP0_VM0
            return self.pv_service.find_by_uuid(self.si, '4236d4e4-f36a-9bf5-1d61-7c31e9059cfc')

        self.logger.info(PERFORMANCE_TEST.format('test_find_by_uuid_without_path_nested_object', START))
        runner = PerfMethodWrapper(action,
                                   'test_find_by_uuid_without_path_nested_object',
                                   self.logger)
        runner.run(N_RUNS)
        self.logger.info(PERFORMANCE_TEST.format('test_find_by_uuid_without_path_nested_object', END))

    def test_find_by_uuid_without_path_flat_object(self):
        def action():
            # vm name = DC0_C0_RP10_VM20
            return self.pv_service.find_by_uuid(self.si, '423634ae-0188-ff08-a60a-83f1b43a2cc4')

        self.logger.info(PERFORMANCE_TEST.format('test_find_by_uuid_without_path_flat_object', START))
        runner = PerfMethodWrapper(action,
                                   'test_find_by_uuid_without_path',
                                   self.logger)
        runner.run(N_RUNS)
        self.logger.info(PERFORMANCE_TEST.format('test_find_by_uuid_without_path_flat_object', END))

    def test_search_by_name_flat_object(self):
        def action():
            return self.pv_service.find_vm_by_name(self.si, 'DC0', 'DC0_C0_RP10_VM24')

        self.logger.info(PERFORMANCE_TEST.format('find_vm_by_name', START))
        runner = PerfMethodWrapper(action,
                                   'search_by_name_flat_object',
                                   self.logger)
        runner.run(N_RUNS)
        self.logger.info(PERFORMANCE_TEST.format('find_vm_by_name', END))
