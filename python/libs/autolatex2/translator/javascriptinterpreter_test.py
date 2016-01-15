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
from autolatex2.translator.javascriptinterpreter import TranslatorInterpreter

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
		if shutil.which('js') is not None:
			self.assertTrue(self.interpreter.runnable)
		else:
			self.assertFalse(self.interpreter.runnable)

	@unittest.skipUnless(shutil.which('js') is not None, "Javascript interpreter not installed")
	def test_run_valid1(self):
		(sout, serr, sex, retcode) = self.interpreter.run('var myvar = \'abc\'')
		self.assertEqual('', sout)
		self.assertEqual('', serr)
		self.assertIsNone(sex)
		self.assertEqual(0, retcode)

	@unittest.skipUnless(shutil.which('js') is not None, "Javascript interpreter not installed")
	def test_run_valid2(self):
		(sout, serr, sex, retcode) = self.interpreter.run('var myvar = \'abc\'; process.stdout.write(myvar)')
		self.assertEqual('abc', sout)
		self.assertEqual('', serr)
		self.assertIsNone(sex)
		self.assertEqual(0, retcode)

	@unittest.skipUnless(shutil.which('js') is not None, "Javascript interpreter not installed")
	def test_run_valid3(self):
		(sout, serr, sex, retcode) = self.interpreter.run('var myvar = \'abc\'; process.stderr.write(myvar)')
		self.assertEqual('', sout)
		self.assertEqual('abc', serr)
		self.assertIsNone(sex)
		self.assertEqual(0, retcode)

	@unittest.skipUnless(shutil.which('js') is not None, "Javascript interpreter not installed")
	def test_run_valid4(self):
		(sout, serr, sex, retcode) = self.interpreter.run('throw "error"')
		self.assertEqual('', sout)
		self.assertEqual('\n[stdin]:4\nthrow "error"\n^\nerror\n', serr)
		self.assertIsInstance(sex, CommandExecutionError)
		self.assertNotEqual(0, sex.errno)
		self.assertNotEqual(0, retcode)
		self.assertEqual(sex.errno, retcode)

	@unittest.skipUnless(shutil.which('js') is not None, "Javascript interpreter not installed")
	def test_run_invalid1(self):
		(sout, serr, sex, retcode) = self.interpreter.run('process.stderr.write(1')
		self.assertEqual('', sout)
		self.assertEqual('\n[stdin]:4\nprocess.stderr.write(1\n                      \nSyntaxError: Unexpected end of input\n    at Object.<anonymous> ([stdin]-wrapper:6:22)\n    at Module._compile (module.js:456:26)\n    at evalScript (node.js:532:25)\n    at Socket.<anonymous> (node.js:154:11)\n    at Socket.EventEmitter.emit (events.js:117:20)\n    at _stream_readable.js:920:16\n    at process._tickCallback (node.js:415:13)\n', serr)
		self.assertIsInstance(sex, CommandExecutionError)
		self.assertNotEqual(0, sex.errno)
		self.assertNotEqual(0, retcode)
		self.assertEqual(sex.errno, retcode)




if __name__ == '__main__':
    unittest.main()

