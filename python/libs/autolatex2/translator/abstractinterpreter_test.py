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


import unittest
import logging

from autolatex2.translator.abstractinterpreter import *

class TestAbstractTranslatorInterpreter(unittest.TestCase):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.__interpreter = None

	def setUp(self):
		logging.getLogger().setLevel(logging.CRITICAL)
		self.__interpreter = AbstractTranslatorInterpreter()

	@property
	def interpreter(self):
		return self.__interpreter




	def test_parent_getter(self):
		self.assertIsNone(self.interpreter.parent)

	def test_parent_setter(self):
		p = AbstractTranslatorInterpreter()
		self.interpreter.parent = p
		self.assertEqual(p, self.interpreter.parent)



	def test_globalVariables(self):
		self.assertFalse('foo' in self.interpreter.globalVariables)
		self.interpreter.globalVariables['foo'] = 'abc'
		self.assertEqual('abc', self.interpreter.globalVariables['foo'])
		self.interpreter.globalVariables['foo'] = ''
		self.assertEqual('', self.interpreter.globalVariables['foo'])
		self.interpreter.globalVariables['foo'] = None
		self.assertIsNone(self.interpreter.globalVariables['foo'])




	def test_runnable(self):
		with self.assertRaises(NotImplementedError):
			self.interpreter.runnable



	def test_run(self):
		with self.assertRaises(NotImplementedError):
			self.interpreter.run('abc')




	def test_toPython_scalar(self):
		self.assertEqual('1', self.interpreter.toPython(1))
		self.assertEqual('\'abc\'', self.interpreter.toPython('abc'))
		self.assertEqual('"abc\'def"', self.interpreter.toPython('abc\'def'))
		self.assertEqual('\'abc"def\'', self.interpreter.toPython('abc"def'))
		self.assertEqual('\'abc"def\\\'ghi\'', self.interpreter.toPython('abc"def\'ghi'))

	def test_toPython_list(self):
		self.assertEqual('[1, 2, 3]', self.interpreter.toPython([1,2,3]))
		self.assertEqual('[1, 2, [3, 4, 5, 6]]', self.interpreter.toPython([1,2,[3,4,5,6]]))

	def test_toPython_set(self):
		self.assertEqual('{1, 2, 3}', self.interpreter.toPython({1,2,3}))

	def test_toPython_dict(self):
		self.assertEqual('{1: 2, 3: 4}', self.interpreter.toPython({1:2,3:4}))






if __name__ == '__main__':
    unittest.main()

