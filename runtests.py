import re
import nose
import nose.config
import sys
from nose.plugins.manager import DefaultPluginManager
c = nose.config.Config()
c.plugins=DefaultPluginManager()
c.srcDirs = ['package']


# c.ignoreFiles.append('vm_autoload_driver')
c.ignoreFiles.append(re.compile(r'^vm_autoload_driver\.py$'))
c.ignoreFiles.append(re.compile(r'^test_get_inventory\.py$'))
c.ignoreFiles.append(re.compile(r'^DeployAppOrchestrationDriver$'))


if not nose.run(config=c):
    sys.exit(1)
