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

from autolatex2.tex.utils import *

import autolatex2.utils.utilfunctions as genutils

class TestUtils(unittest.TestCase):

	def setUp(self):
		logging.getLogger().setLevel(logging.CRITICAL)



	def test_getTeXFileExtensions(self):
		self.assertEqual(['.tex', '.latex', '.ltx'], getTeXFileExtensions())

	def test_isTeXFileExtension(self):
		self.assertTrue(isTeXFileExtension('.tex'))
		self.assertTrue(isTeXFileExtension('.latex'))
		self.assertTrue(isTeXFileExtension('.ltx'))
		self.assertTrue(isTeXFileExtension('.TeX'))
		self.assertTrue(isTeXFileExtension('.LaTeX'))
		self.assertFalse(isTeXFileExtension('.doc'))

	def test_isTeXdocument(self):
		self.assertTrue(isTeXDocument('file.tex'))
		self.assertTrue(isTeXDocument('file.latex'))
		self.assertTrue(isTeXDocument('file.ltx'))
		self.assertTrue(isTeXDocument('file.TeX'))
		self.assertTrue(isTeXDocument('file.LaTeX'))
		self.assertFalse(isTeXDocument('file.doc'))

	def test_extractTeXWarningFromLine_00(self):
		wset = set()
		self.assertTrue(extractTeXWarningFromLine('\n\nWarning: There were undefined references. re-run the LaTeX compiler', wset))
		self.assertEqual(set([]), wset)
	
	def test_extractTeXWarningFromLine_01(self):
		wset = set()
		self.assertFalse(extractTeXWarningFromLine('\n\nWarning: There were undefined references', wset))
		self.assertEqual(set([TeXWarnings.undefined_reference]), wset)

	def test_extractTeXWarningFromLine_02(self):
		wset = set()
		self.assertFalse(extractTeXWarningFromLine('\n\nWarning: Citation XYZ undefined', wset))
		self.assertEqual(set([TeXWarnings.undefined_citation]), wset)

	def test_extractTeXWarningFromLine_03(self):
		wset = set()
		self.assertFalse(extractTeXWarningFromLine('\n\nWarning: There were multiply-defined labels', wset))
		self.assertEqual(set([TeXWarnings.multiple_definition]), wset)

	def test_extractTeXWarningFromLine_04(self):
		wset = set()
		self.assertFalse(extractTeXWarningFromLine('\n\nWarning: This is a warning', wset))
		self.assertEqual(set([TeXWarnings.other_warning]), wset)

	def test_parseTeXLogFile_noFatal(self):
		filename = genutils.findFileInPath("test1.txt")
		self.assertIsNotNone(filename)
		(fatalError, blocks) = parseTeXLogFile(filename)
		self.assertEqual('', fatalError)
		self.assertEqual(164, len(blocks))

	def test_parseTeXLogFile_fatal(self):
		filename = genutils.findFileInPath("test2.txt")
		self.assertIsNotNone(filename)
		(fatalError, blocks) = parseTeXLogFile(filename)
		self.assertTrue(fatalError.startswith("Undefined control sequence."))
		self.assertEqual(42, len(blocks))



if __name__ == '__main__':
    unittest.main()

