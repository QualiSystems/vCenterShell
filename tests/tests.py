import sys
sys.path.append("/")

import unittest
from teamcity import is_running_under_teamcity
from teamcity.unittestpy import TeamcityTestRunner

if __name__ == '__main__':
    if is_running_under_teamcity():
        runner = TeamcityTestRunner()
    else:
        runner = unittest.TextTestRunner()

    loader = unittest.TestLoader()
    loader.testMethodPrefix = 'test_'
    suite = loader.discover("", pattern='test*.py')

    allTests = unittest.TestSuite(suite)
    runner.run(allTests)
