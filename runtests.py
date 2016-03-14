import nose
import nose.config

c = nose.config.Config()
c.srcDirs = ['package']
nose.run(config=c)