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

from autolatex2.translator.abstractinterpreter import *

from autolatex2.utils import debug

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




	def test_runPython_valid1(self):
		(sout, serr, sex) = self.interpreter.runPython('myvar = \'abc\'')
		self.assertEqual('', sout)
		self.assertEqual('', serr)
		self.assertIsNone(sex)

	def test_runPython_valid2(self):
		(sout, serr, sex) = self.interpreter.runPython('myvar = \'abc\'\nprint(myvar)')
		self.assertEqual('abc\n', sout)
		self.assertEqual('', serr)
		self.assertIsNone(sex)

	def test_runPython_valid3(self):
		(sout, serr, sex) = self.interpreter.runPython('myvar = \'abc\'\nsys.stderr.write(myvar)')
		self.assertEqual('', sout)
		self.assertEqual('abc', serr)
		self.assertIsNone(sex)

	def test_runPython_valid4(self):
		with self.assertRaises(NotImplementedError):
			self.interpreter.runPython('raise NotImplementedError')

	def test_runPython_valid5(self):
		with self.assertRaises(NotImplementedError):
			self.interpreter.runPython('raise NotImplementedError', False)

	def test_runPython_valid6(self):
		(sout, serr, sex) = self.interpreter.runPython('raise NotImplementedError', True)
		self.assertEqual('', sout)
		self.assertEqual('', serr)
		self.assertIsInstance(sex, NotImplementedError)

	def test_runPython_invalid1(self):
		with self.assertRaises(SyntaxError):
			self.interpreter.runPython('print(1')

	def test_runPython_invalid2(self):
		with self.assertRaises(SyntaxError):
			self.interpreter.runPython('print(1', False)

	def test_runPython_invalid3(self):
		(sout, serr, sex) = self.interpreter.runPython('print(1', True)
		self.assertEqual('', sout)
		self.assertEqual('', serr)
		self.assertIsInstance(sex, SyntaxError)



	def test_runCommand_valid1(self):
		(sout, serr, sex) = self.interpreter.runCommand('python', '-c', 'print 123')
		self.assertEqual('123\n', sout)
		self.assertEqual('', serr)
		self.assertIsNone(sex)

	def test_runCommand_valid2(self):
		(sout, serr, sex) = self.interpreter.runCommand('python', '-c', 'import sys;sys.stderr.write(\'123\\n\')')
		self.assertEqual('', sout)
		self.assertEqual('123\n', serr)
		self.assertIsNone(sex)

	def test_runCommand_invalid1(self):
		(sout, serr, sex) = self.interpreter.runCommand('python', '-c', 'sys.stderr.write(\'123\\n\')')
		self.assertEqual('', sout)
		self.assertEqual('Traceback (most recent call last):\n  File "<string>", line 1, in <module>\nNameError: name \'sys\' is not defined\n', serr)
		self.assertIsInstance(sex, CommandExecutionError)
		self.assertNotEqual(0, sex.errno)



	def test_runScript_valid1(self):
		script = 'print 123'
		(sout, serr, sex) = self.interpreter.runScript(script, 'python', '-')
		self.assertEqual('123\n', sout)
		self.assertEqual('', serr)
		self.assertIsNone(sex)

	def test_runScript_valid2(self):
		script = 'import sys;sys.stderr.write(\'123\\n\')'
		(sout, serr, sex) = self.interpreter.runScript(script, 'python', '-')
		self.assertEqual('', sout)
		self.assertEqual('123\n', serr)
		self.assertIsNone(sex)

	def test_runScript_invalid1(self):
		script = 'sys.stderr.write(\'123\\n\')'
		(sout, serr, sex) = self.interpreter.runScript(script, 'python', '-')
		self.assertEqual('', sout)
		self.assertEqual('Traceback (most recent call last):\n  File "<stdin>", line 1, in <module>\nNameError: name \'sys\' is not defined\n', serr)
		self.assertIsInstance(sex, CommandExecutionError)
		self.assertNotEqual(0, sex.errno)




if __name__ == '__main__':
    unittest.main()

