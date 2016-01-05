import os

import os.path
import sys
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), '../'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../vCenterShell'))
from common.logger.service import LoggingService


class TestLoggingService(unittest.TestCase):
    def test_logging_service_01(self):
        log_file_name = "test_log.log"
        LoggingService("CRITICAL", "DEBUG", None)
        self.assertFalse(os.path.isfile(log_file_name))

        # LoggingService("CRITICAL", "DEBUG", log_file_name)
        # self.assertTrue(os.path.isfile(log_file_name))
        # os.unlink(log_file_name)

    def test_logging_service_02(self):
        log_file_name = "test_log.log"
        LoggingService("DEBUG", "CRITICAL", None)
        self.assertFalse(os.path.isfile(log_file_name))
        # LoggingService("DEBUG", "CRITICAL", log_file_name)
        # self.assertTrue(os.path.isfile(log_file_name))
        # self.assertEquals(os.path.getsize(log_file_name), 0)
        # os.unlink(log_file_name)
