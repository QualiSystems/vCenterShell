import nose
import nose.config
import sys
from nose.plugins.manager import DefaultPluginManager
c = nose.config.Config()
c.plugins=DefaultPluginManager()
c.srcDirs = ['package']
if not nose.run(config=c):
    sys.exit(1)
