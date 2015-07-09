#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2015  Stephane Galland <galland@arakhne.org>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.


import unittest
import logging

from autolatex2.utils.utils import *

from autolatex2.utils import debug

class TestUtils(unittest.TestCase):

	def setUp(self):
		logging.getLogger().setLevel(logging.CRITICAL)



	def test_firstOf(self):
		self.assertEqual('a', firstOf('a', 'b', 'c'))
		self.assertEqual('a', firstOf(None, 'a', 'b', 'c'))
		self.assertEqual('a', firstOf(None, 'a', None, 'b', 'c'))
		self.assertEqual('a', firstOf(None, None, 'a', None, 'b', 'c'))

	def test_basename_inline(self):
		self.assertEqual('name', basename('name.ext', '.ext'))
		self.assertEqual('name', basename('name.ext', '.ext', '.a'))
		self.assertEqual('name', basename('name.ext', '.a', '.ext'))
		self.assertEqual('name.ext', basename('name.ext', '.a'))
		self.assertEqual('name.ext', basename('name.ext'))

	def test_basename_tuple(self):
		self.assertEqual('name', basename('name.ext', ('.ext')))
		self.assertEqual('name', basename('name.ext', ('.ext', '.a')))
		self.assertEqual('name', basename('name.ext', ('.a', '.ext')))
		self.assertEqual('name.ext', basename('name.ext', ('.a')))

	def test_basename_list(self):
		self.assertEqual('name', basename('name.ext', [ '.ext' ]))
		self.assertEqual('name', basename('name.ext', ['.ext', '.a' ]))
		self.assertEqual('name', basename('name.ext', ['.a', '.ext' ]))

	def test_basename_set(self):
		self.assertEqual('name', basename('name.ext', { '.ext' }))
		self.assertEqual('name', basename('name.ext', {'.ext', '.a' }))
		self.assertEqual('name', basename('name.ext', {'.a', '.ext' }))

	def test_parseCLI_noException(self):
		environment = { 'a': 'va', 'b': 'vb', 'c': 'vc' }
		self.assertListEqual([], parseCLI('', environment))
		self.assertListEqual([ 'abc', '--def', 'ghi' ], parseCLI('abc --def ghi', environment))
		self.assertListEqual([ 'abc', '--def', 'ghi' ], parseCLI('abc --def ${z} ghi', environment))
		self.assertListEqual([ 'abc', '--def', 'va', 'ghi' ], parseCLI('abc --def $a ghi', environment))
		self.assertListEqual([ 'abc', '--def', 'vbbc', 'ghi' ], parseCLI('abc --def ${b}bc ghi', environment))
		self.assertListEqual([ 'abc', os.path.expanduser('~') ], parseCLI('abc $HOME', environment))

	def test_parseCLI_exception(self):
		environment = { 'a': 'va', 'b': 'vb', 'c': 'vc' }
		exception = { 'b' }
		self.assertListEqual([], parseCLI('', environment, exception))
		self.assertListEqual([ 'abc', '--def', 'ghi' ], parseCLI('abc --def ghi', environment, exception))
		self.assertListEqual([ 'abc', '--def', 'ghi' ], parseCLI('abc --def ${z} ghi', environment, exception))
		self.assertListEqual([ 'abc', '--def', 'va', 'ghi' ], parseCLI('abc --def $a ghi', environment, exception))
		self.assertListEqual([ 'abc', '--def', '${b}bc', 'ghi' ], parseCLI('abc --def ${b}bc ghi', environment, exception))
		self.assertListEqual([ 'abc', os.path.expanduser('~') ], parseCLI('abc $HOME', environment, exception))


if __name__ == '__main__':
    unittest.main()

