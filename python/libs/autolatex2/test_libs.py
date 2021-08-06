import unittest
import sys
import os

# Discover tests and run them
def discover_and_run(start_dir : str = '.', pattern : str = '*_test.py') :
		loader = unittest.TestLoader()
		tests = loader.discover(start_dir,  pattern)
		testRunner = unittest.runner.TextTestRunner()
		results = testRunner.run(tests)
		return results
	
# Update the python path with the folder containing the testing data
script_dir = os.path.dirname(__file__)
test_data_dir = os.path.join(script_dir,  'dev-resources')
sys.path.insert(0, test_data_dir)

# Do the tests
results = discover_and_run()

nbErrors = len(results.errors)
nbFailures = len(results.failures)

if nbErrors > 0 or nbFailures > 0:
	sys.exit(255)
else:
	sys.exit(0)
