import nose
import nose.config
from nose.plugins.manager import DefaultPluginManager
c = nose.config.Config()
c.plugins=DefaultPluginManager()
c.srcDirs = ['package']
nose.run(config=c)