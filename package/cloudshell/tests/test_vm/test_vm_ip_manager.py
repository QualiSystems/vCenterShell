from unittest import TestCase

import re

from mock import Mock, patch

from cloudshell.cp.vcenter.commands.ip_result import IpResult, IpReason
from cloudshell.cp.vcenter.vm.ip_manager import VMIPManager

counter = 0


class TestVMIPManager(TestCase):
    def setUp(self):
        self.ip_manager = VMIPManager()
        self.ip_manager.INTERVAL = 0.001
        self.default_net = 'aa'
        self.function = re.compile('.*').match
        self.cancel = Mock()
        self.cancel.is_cancelled = None
        self.timeout = 1
        self.logger = Mock()
        self.vm = Mock()
        self.vm.guest = Mock()
        self.vm.guest.toolsStatus = 'running'

    def test_get_match_method_none(self):
        method = self.ip_manager.get_ip_match_function(None)
        self.assertEqual(method, re.compile('.*').match)

    def test_get_match_method(self):
        method = self.ip_manager.get_ip_match_function('1.*')
        self.assertEqual(method, re.compile('1.*').match)

    def test_get_ip_toolsNotInstalled(self):
        vm = Mock()
        vm.guest = Mock()
        vm.guest.toolsStatus = 'toolsNotInstalled'
        self.assertRaises(ValueError,
                          self.ip_manager.get_ip,
                          vm,
                          self.default_net,
                          self.function,
                          self.cancel,
                          self.timeout,
                          self.logger)

    def test_get_ip_no_timeout_no_found(self):
        self.vm.guest.ipAddress = None
        self.vm.guest.net = []
        res = self.ip_manager.get_ip(
            self.vm,
            self.default_net,
            self.function,
            self.cancel,
            None,
            self.logger)
        expected = IpResult(None, IpReason.NotFound)
        self.assertEqual(expected.ip_address, res.ip_address)
        self.assertIsNone(res.ip_address)
        self.assertEqual(expected.reason, res.reason)

    def test_get_ip_no_timeout_found(self):
        self.vm.guest.ipAddress = '1.1.1.1'
        self.vm.guest.net = []
        res = self.ip_manager.get_ip(
            self.vm,
            self.default_net,
            self.function,
            self.cancel,
            None,
            self.logger)
        expected = IpResult('1.1.1.1', IpReason.Success)
        self.assertEqual(expected.ip_address, res.ip_address)
        self.assertEqual(expected.reason, res.reason)

    def test_get_ip_no_timeout_multi_ip_regex_pattern(self):
        self.vm.guest.ipAddress = '1.1.1.1'
        nic = Mock()
        nic.network = None
        nic.ipAddress = ['2.2.2.2']
        self.vm.guest.net = [nic]
        res = self.ip_manager.get_ip(
            self.vm,
            self.default_net,
            self.ip_manager.get_ip_match_function('^2\.2\.2\.2$'),
            self.cancel,
            None,
            self.logger)
        expected = IpResult('2.2.2.2', IpReason.Success)
        self.assertEqual(expected.ip_address, res.ip_address)
        self.assertEqual(expected.reason, res.reason)

    def test_get_ip_with_timeout(self):
        TestVMIPManager.counter = 0
        self.ip_manager._obtain_ip = TestVMIPManager.mock_func

        res = self.ip_manager.get_ip(
            self.vm,
            self.default_net,
            self.function,
            self.cancel,
            self.timeout,
            self.logger)
        expected = IpResult('1.1.1.1', IpReason.Success)
        self.assertEqual(expected.ip_address, res.ip_address)
        self.assertEqual(expected.reason, res.reason)

    def test_get_ip_with_timeout_raised(self):
        TestVMIPManager.counter = 0
        self.ip_manager._obtain_ip = TestVMIPManager.mock_func
        self.ip_manager.INTERVAL = 1.1

        res = self.ip_manager.get_ip(
            self.vm,
            self.default_net,
            self.function,
            self.cancel,
            self.timeout,
            self.logger)
        expected = IpResult(None, IpReason.Timeout)
        self.assertEqual(expected.ip_address, res.ip_address)
        self.assertEqual(expected.reason, res.reason)
        self.ip_manager.INTERVAL = 0.001

    def test_get_ip_cancelled(self):
        TestVMIPManager.counter = 0
        cancel = Mock()
        cancel.is_cancelled = True

        res = self.ip_manager.get_ip(
            self.vm,
            self.default_net,
            self.function,
            cancel,
            self.timeout,
            self.logger)
        expected = IpResult(None, IpReason.Cancelled)
        self.assertEqual(expected.ip_address, res.ip_address)
        self.assertEqual(expected.reason, res.reason)
    counter = 0

    @staticmethod
    def mock_func(*args):
        if TestVMIPManager.counter:
            return '1.1.1.1'
        TestVMIPManager.counter += 1
