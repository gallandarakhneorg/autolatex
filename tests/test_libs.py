#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 1998-2021 Stephane Galland <galland@arakhne.org>
#
# This program is free library; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation; either version 3 of the
# License, or any later version.
#
# This library is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; see the file COPYING.  If not,
# write to the Free Software Foundation, Inc., 59 Temple Place - Suite
# 330, Boston, MA 02111-1307, USA.

import unittest
import sys
import os

TEST_TO_RUN = [
	'bug109'
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
