# -*- coding: utf-8 -*-
"""
Pretty much trivial logging demo

Default log file - './logs/vCenter.log'
"""

from vCenterShell.pycommon.logger import getLogger
from vCenterShell.pycommon.logger import configure_loglevel

_logger = getLogger(__name__)           # Default logger is using
# _logger = getLogger("vCenterShell")     # for Shell App itself
# _logger = getLogger("vCenterCommon")    # for Common Utilises

# ONLY IF YOU WANTED CONFIGURE LOG MANUALLY
configure_loglevel("INFO", "INFO", "../../logs/vCenter.log")

if __name__ == "__main__":
    _logger.debug("DEBUG SHOULD BE SKIPPED")
    _logger.info("INFO IS OK")
    _logger.warn("WARNING IS OK")
    _logger.error("ERROR IS OK!!!")
    _logger.critical("CRITICAL IS OK ?!!!!")