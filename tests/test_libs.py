import unittest
import sys
import os

TEST_TO_RUN = [
	#'runner'
]

# Discover tests and run them
def discover_and_run(start_dir : str, pattern : str = '*_test.py') :
		loader = unittest.TestLoader()
		tests = loader.discover(start_dir,  pattern)
		testRunner = unittest.runner.TextTestRunner()
		results = testRunner.run(tests)
		return results
	
script_dir = os.path.dirname(__file__)

# Update the python path with the folder of the main source-code
main_src_dir = os.path.normpath(os.path.join(script_dir,  '..', 'src'))
sys.path.insert(0, main_src_dir)

# Update the python path with the folder containing the testing data
test_data_dir = os.path.join(script_dir,  'autolatex2tests', 'dev-resources')
sys.path.insert(0, test_data_dir)

# Do the tests
if len(TEST_TO_RUN) == 1:
	results = discover_and_run(os.path.join(script_dir,  'autolatex2tests'),  TEST_TO_RUN[0] + '_test.py')
else:
	results = discover_and_run(os.path.join(script_dir,  'autolatex2tests'))

nbErrors = len(results.errors)
nbFailures = len(results.failures)

if nbErrors > 0 or nbFailures > 0:
	sys.exit(255)
else:
	sys.exit(0)
