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
import shutil

from autolatex2.translator.abstractinterpreter import CommandExecutionError
from autolatex2.translator.rubyinterpreter import TranslatorInterpreter

from autolatex2.utils import debug

class TestTranslatorInterpreter(unittest.TestCase):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.__interpreter = None

	def setUp(self):
		logging.getLogger().setLevel(logging.CRITICAL)
		self.__interpreter = TranslatorInterpreter()

	@property
	def interpreter(self):
		return self.__interpreter


	def test_runnable(self):
		if shutil.which('ruby') is not None:
			self.assertTrue(self.interpreter.runnable)
		else:
			self.assertFalse(self.interpreter.runnable)

	@unittest.skipUnless(shutil.which('ruby') is not None, "Ruby interpreter not installed")
	def test_run_valid1(self):
		(sout, serr, sex) = self.interpreter.run('myvar = \'abc\'')
		self.assertEqual('', sout)
		self.assertEqual('', serr)
		self.assertIsNone(sex)

	@unittest.skipUnless(shutil.which('ruby') is not None, "Ruby interpreter not installed")
	def test_run_valid2(self):
		(sout, serr, sex) = self.interpreter.run('myvar = \'abc\'; puts myvar')
		self.assertEqual('abc\n', sout)
		self.assertEqual('', serr)
		self.assertIsNone(sex)

	@unittest.skipUnless(shutil.which('ruby') is not None, "Ruby interpreter not installed")
	def test_run_valid3(self):
		(sout, serr, sex) = self.interpreter.run('myvar = \'abc\'; $stderr.puts myvar')
		self.assertEqual('', sout)
		self.assertEqual('abc\n', serr)
		self.assertIsNone(sex)

	@unittest.skipUnless(shutil.which('ruby') is not None, "Ruby interpreter not installed")
	def test_run_valid4(self):
		(sout, serr, sex) = self.interpreter.run('raise "error"')
		self.assertEqual('', sout)
		self.assertEqual('-:5:in `<main>\': error (RuntimeError)\n', serr)
		self.assertIsInstance(sex, CommandExecutionError)
		self.assertNotEqual(0, sex.errno)

	@unittest.skipUnless(shutil.which('ruby') is not None, "Ruby interpreter not installed")
	def test_run_invalid1(self):
		(sout, serr, sex) = self.interpreter.run('print (1')
		self.assertEqual('', sout)
		self.assertEqual('-:5: syntax error, unexpected $end, expecting \')\'\nprint (1\n        ^\n', serr)
		self.assertIsInstance(sex, CommandExecutionError)
		self.assertNotEqual(0, sex.errno)




if __name__ == '__main__':
    unittest.main()

