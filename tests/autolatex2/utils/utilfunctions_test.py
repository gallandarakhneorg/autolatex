#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 1998-2021 Stephane Galland <galland@arakhne.org>
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

import os
import unittest
import logging

import autolatex2.utils.utilfunctions as genutils

class TestUtils(unittest.TestCase):

	def setUp(self):
		logging.getLogger().setLevel(logging.CRITICAL)



	def test_firstOf(self):
		self.assertEqual('a', genutils.firstOf('a', 'b', 'c'))
		self.assertEqual('a', genutils.firstOf(None, 'a', 'b', 'c'))
		self.assertEqual('a', genutils.firstOf(None, 'a', None, 'b', 'c'))
		self.assertEqual('a', genutils.firstOf(None, None, 'a', None, 'b', 'c'))

	def test_basename_inline_a(self):
		self.assertEqual('name', genutils.basename('name.ext', '.ext'))
		self.assertEqual('name', genutils.basename('name.ext', '.ext', '.a'))
		self.assertEqual('name', genutils.basename('name.ext', '.a', '.ext'))
		self.assertEqual('name.ext', genutils.basename('name.ext', '.a'))
		self.assertEqual('name.ext', genutils.basename('name.ext'))

	def test_basename_inline_b(self):
		d = os.path.join('a',  'b', 'c')
		act = os.path.join(d,  'name.ext')
		exp = 'name'
		exp2 = 'name.ext'
		self.assertEqual(exp, genutils.basename(act, '.ext'))
		self.assertEqual(exp, genutils.basename(act, '.ext', '.a'))
		self.assertEqual(exp, genutils.basename(act, '.a', '.ext'))
		self.assertEqual(exp2, genutils.basename(act, '.a'))
		self.assertEqual(exp2, genutils.basename(act))

	def test_basename_tuple_a(self):
		self.assertEqual('name', genutils.basename('name.ext', ('.ext')))
		self.assertEqual('name', genutils.basename('name.ext', ('.ext', '.a')))
		self.assertEqual('name', genutils.basename('name.ext', ('.a', '.ext')))
		self.assertEqual('name.ext', genutils.basename('name.ext', ('.a')))

	def test_basename_tuple_b(self):
		d = os.path.join('a',  'b', 'c')
		act = os.path.join(d,  'name.ext')
		exp = 'name'
		exp2 = 'name.ext'
		self.assertEqual(exp, genutils.basename(act, ('.ext')))
		self.assertEqual(exp, genutils.basename(act, ('.ext', '.a')))
		self.assertEqual(exp, genutils.basename(act, ('.a', '.ext')))
		self.assertEqual(exp2, genutils.basename(act, ('.a')))

	def test_basename_list_a(self):
		self.assertEqual('name', genutils.basename('name.ext', [ '.ext' ]))
		self.assertEqual('name', genutils.basename('name.ext', ['.ext', '.a' ]))
		self.assertEqual('name', genutils.basename('name.ext', ['.a', '.ext' ]))

	def test_basename_list_b(self):
		d = os.path.join('a',  'b', 'c')
		act = os.path.join(d,  'name.ext')
		exp = 'name'
		self.assertEqual(exp, genutils.basename(act, [ '.ext' ]))
		self.assertEqual(exp, genutils.basename(act, ['.ext', '.a' ]))
		self.assertEqual(exp, genutils.basename(act, ['.a', '.ext' ]))

	def test_basename_set_a(self):
		self.assertEqual('name', genutils.basename('name.ext', { '.ext' }))
		self.assertEqual('name', genutils.basename('name.ext', {'.ext', '.a' }))
		self.assertEqual('name', genutils.basename('name.ext', {'.a', '.ext' }))

	def test_basename_set_b(self):
		d = os.path.join('a',  'b', 'c')
		act = os.path.join(d,  'name.ext')
		exp = 'name'
		self.assertEqual(exp, genutils.basename(act, { '.ext' }))
		self.assertEqual(exp, genutils.basename(act, {'.ext', '.a' }))
		self.assertEqual(exp, genutils.basename(act, {'.a', '.ext' }))

	def test_basename2_inline_a(self):
		self.assertEqual('name', genutils.basename2('name.ext', '.ext'))
		self.assertEqual('name', genutils.basename2('name.ext', '.ext', '.a'))
		self.assertEqual('name', genutils.basename2('name.ext', '.a', '.ext'))
		self.assertEqual('name.ext', genutils.basename2('name.ext', '.a'))
		self.assertEqual('name.ext', genutils.basename2('name.ext'))

	def test_basename2_inline_b(self):
		d = os.path.join('a',  'b', 'c')
		act = os.path.join(d,  'name.ext')
		exp = os.path.join(d,  'name')
		exp2 = os.path.join(d,  'name.ext')
		self.assertEqual(exp, genutils.basename2(act, '.ext'))
		self.assertEqual(exp, genutils.basename2(act, '.ext', '.a'))
		self.assertEqual(exp, genutils.basename2(act, '.a', '.ext'))
		self.assertEqual(exp2, genutils.basename2(act, '.a'))
		self.assertEqual(exp2, genutils.basename2(act))

	def test_basename2_tuple_a(self):
		self.assertEqual('name', genutils.basename2('name.ext', ('.ext')))
		self.assertEqual('name', genutils.basename2('name.ext', ('.ext', '.a')))
		self.assertEqual('name', genutils.basename2('name.ext', ('.a', '.ext')))
		self.assertEqual('name.ext', genutils.basename2('name.ext', ('.a')))

	def test_basename2_tuple_b(self):
		d = os.path.join('a',  'b', 'c')
		act = os.path.join(d,  'name.ext')
		exp = os.path.join(d,  'name')
		exp2 = os.path.join(d,  'name.ext')
		self.assertEqual(exp, genutils.basename2(act, ('.ext')))
		self.assertEqual(exp, genutils.basename2(act, ('.ext', '.a')))
		self.assertEqual(exp, genutils.basename2(act, ('.a', '.ext')))
		self.assertEqual(exp2, genutils.basename2(act, ('.a')))

	def test_basename2_list_a(self):
		self.assertEqual('name', genutils.basename2('name.ext', [ '.ext' ]))
		self.assertEqual('name', genutils.basename2('name.ext', ['.ext', '.a' ]))
		self.assertEqual('name', genutils.basename2('name.ext', ['.a', '.ext' ]))

	def test_basename2_list_b(self):
		d = os.path.join('a',  'b', 'c')
		act = os.path.join(d,  'name.ext')
		exp = os.path.join(d,  'name')
		self.assertEqual(exp, genutils.basename2(act, [ '.ext' ]))
		self.assertEqual(exp, genutils.basename2(act, ['.ext', '.a' ]))
		self.assertEqual(exp, genutils.basename2(act, ['.a', '.ext' ]))

	def test_basename2_set_a(self):
		self.assertEqual('name', genutils.basename2('name.ext', { '.ext' }))
		self.assertEqual('name', genutils.basename2('name.ext', {'.ext', '.a' }))
		self.assertEqual('name', genutils.basename2('name.ext', {'.a', '.ext' }))

	def test_basename2_set_b(self):
		d = os.path.join('a',  'b', 'c')
		act = os.path.join(d,  'name.ext')
		exp = os.path.join(d,  'name')
		self.assertEqual(exp, genutils.basename2(act, { '.ext' }))
		self.assertEqual(exp, genutils.basename2(act, {'.ext', '.a' }))
		self.assertEqual(exp, genutils.basename2(act, {'.a', '.ext' }))

	def test_parseCLI_noException(self):
		environment = { 'a': 'va', 'b': 'vb', 'c': 'vc' }
		self.assertListEqual([], genutils.parseCLI('', environment))
		self.assertListEqual([ 'abc', '--def', 'ghi' ], genutils.parseCLI('abc --def ghi', environment))
		self.assertListEqual([ 'abc', '--def', 'ghi' ], genutils.parseCLI('abc --def ${z} ghi', environment))
		self.assertListEqual([ 'abc', '--def', 'va', 'ghi' ], genutils.parseCLI('abc --def $a ghi', environment))
		self.assertListEqual([ 'abc', '--def', 'vbbc', 'ghi' ], genutils.parseCLI('abc --def ${b}bc ghi', environment))
		self.assertListEqual([ 'abc', os.path.expanduser('~') ], genutils.parseCLI('abc $HOME', environment))

	def test_parseCLI_exception(self):
		environment = { 'a': 'va', 'b': 'vb', 'c': 'vc' }
		exception = { 'b' }
		self.assertListEqual([], genutils.parseCLI('', environment, exception))
		self.assertListEqual([ 'abc', '--def', 'ghi' ], genutils.parseCLI('abc --def ghi', environment, exception))
		self.assertListEqual([ 'abc', '--def', 'ghi' ], genutils.parseCLI('abc --def ${z} ghi', environment, exception))
		self.assertListEqual([ 'abc', '--def', 'va', 'ghi' ], genutils.parseCLI('abc --def $a ghi', environment, exception))
		self.assertListEqual([ 'abc', '--def', '${b}bc', 'ghi' ], genutils.parseCLI('abc --def ${b}bc ghi', environment, exception))
		self.assertListEqual([ 'abc', os.path.expanduser('~') ], genutils.parseCLI('abc $HOME', environment, exception))


if __name__ == '__main__':
    unittest.main()

