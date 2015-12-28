import sys
import unittest

sys.path.append("/")
sys.path.append("../")

if __name__ == '__main__':
    runner = unittest.TextTestRunner()

    loader = unittest.TestLoader()
    loader.testMethodPrefix = 'test_'
    suite = loader.discover("", pattern='test*.py')

    allTests = unittest.TestSuite(suite)
    runner.run(allTests)
