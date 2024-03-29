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
import shutil

from autolatex2.translator.interpreters.abstractinterpreter import CommandExecutionError
from autolatex2.translator.interpreters.shinterpreter import TranslatorInterpreter
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
		if shutil.which('sh') is not None:
			self.assertTrue(self.interpreter.runnable)
		else:
			self.assertFalse(self.interpreter.runnable)

	@unittest.skipUnless(shutil.which('sh') is not None, "Shell interpreter not installed")
	def test_run_valid1(self):
		(sout, serr, sex, retcode) = self.interpreter.run('MYVAR=\'abc\'')
		self.assertEqual('', sout)
		self.assertEqual('', serr)
		self.assertIsNone(sex)
		self.assertEqual(0, retcode)

	@unittest.skipUnless(shutil.which('sh') is not None, "Shell interpreter not installed")
	def test_run_valid2(self):
		(sout, serr, sex, retcode) = self.interpreter.run('MYVAR=\'abc\'; echo $MYVAR')
		self.assertEqual('abc\n', sout)
		self.assertEqual('', serr)
		self.assertIsNone(sex)
		self.assertEqual(0, retcode)

	@unittest.skipUnless(shutil.which('sh') is not None, "Shell interpreter not installed")
	def test_run_valid3(self):
		(sout, serr, sex, retcode) = self.interpreter.run('MYVAR=\'abc\'; echo $MYVAR >&2')
		self.assertEqual('', sout)
		self.assertEqual('abc\n', serr)
		self.assertIsNone(sex)
		self.assertEqual(0, retcode)

	@unittest.skipUnless(shutil.which('sh') is not None, "Shell interpreter not installed")
	def test_run_valid4(self):
		(sout, serr, sex, retcode) = self.interpreter.run('false')
		self.assertEqual('', sout)
		self.assertEqual('', serr)
		self.assertIsInstance(sex, CommandExecutionError)
		self.assertNotEqual(0, sex.errno)
		self.assertNotEqual(0, retcode)
		self.assertEqual(sex.errno, retcode)

	@unittest.skipUnless(shutil.which('sh') is not None, "Shell interpreter not installed")
	def test_run_invalid1(self):
		(sout, serr, sex, retcode) = self.interpreter.run('echo (1')
		self.assertEqual('', sout)
		self.assertEqual('sh: 5: Syntax error: word unexpected (expecting ")")\n', serr)
		self.assertIsInstance(sex, CommandExecutionError)
		self.assertNotEqual(0, sex.errno)
		self.assertNotEqual(0, retcode)
		self.assertEqual(sex.errno, retcode)




if __name__ == '__main__':
    unittest.main()

