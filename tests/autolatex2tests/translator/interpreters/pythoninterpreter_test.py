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
import logging

from autolatex2.translator.interpreters.pythoninterpreter import TranslatorInterpreter
from autolatex2.config.configobj import Config

class TestTranslatorInterpreter(unittest.TestCase):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.__interpreter = None
		self.__config = Config()

	def setUp(self):
		logging.getLogger().setLevel(logging.CRITICAL)
		self.__interpreter = TranslatorInterpreter(self.__config)

	@property
	def interpreter(self):
		return self.__interpreter



	def test_runnable(self):
		self.assertTrue(self.interpreter.runnable)



	def test_run_valid1(self):
		(sout, serr, sex, retcode) = self.interpreter.run('myvar = \'abc\'')
		self.assertEqual('', sout)
		self.assertEqual('', serr)
		self.assertIsNone(sex)
		self.assertEqual(0, retcode)

	def test_run_valid2(self):
		(sout, serr, sex, retcode) = self.interpreter.run('myvar = \'abc\'\nprint(myvar)')
		self.assertEqual('abc\n', sout)
		self.assertEqual('', serr)
		self.assertIsNone(sex)
		self.assertEqual(0, retcode)

	def test_run_valid3(self):
		(sout, serr, sex, retcode) = self.interpreter.run('myvar = \'abc\'\nsys.stderr.write(myvar)')
		self.assertEqual('', sout)
		self.assertEqual('abc', serr)
		self.assertIsNone(sex)
		self.assertEqual(0, retcode)

	def test_run_valid4(self):
		with self.assertRaises(NotImplementedError):
			self.interpreter.run('raise NotImplementedError')

	def test_run_invalid1(self):
		with self.assertRaises(SyntaxError):
			self.interpreter.run(code = 'print(1',  showScriptOnError = False)

	def test_run_invalid2(self):
		with self.assertRaises(SyntaxError):
			self.interpreter.runPython(script = 'print(1', interceptError = False,  showScriptOnError = False)




if __name__ == '__main__':
    unittest.main()

