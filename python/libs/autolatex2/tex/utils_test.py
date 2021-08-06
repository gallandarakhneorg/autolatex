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
		self.assertEqual(0, len(blocks))

	def test_parseTeXLogFile_fatal(self):
		filename = genutils.findFileInPath("test2.txt")
		self.assertIsNotNone(filename)
		(fatalError, blocks) = parseTeXLogFile(filename)
		self.assertEqual('./documentation.tex:209:', fatalError)
		self.assertEqual(1, len(blocks))
		self.assertEqual('] ################ FRAME 13./documentation.tex:209: Undefined control sequence.\\beamer@doifinframe ... text on the slides. \\refa{noref} \\end {itemize} \\en...l.209 \\end{frame}', blocks[0])

	def test_extractErrorMessageFromTeXLogs_noFatal_noExtension(self):
		filename = genutils.findFileInPath("test1.txt")
		self.assertIsNotNone(filename)
		(fatalError, blocks) = parseTeXLogFile(filename)
		errmsg = extractErrorMessageFromTeXLogs(filename, fatalError, blocks, False, '')
		self.assertEqual('', errmsg)

	def test_extractErrorMessageFromTeXLogs_fatal_noExtension(self):
		filename = genutils.findFileInPath("test2.txt")
		self.assertIsNotNone(filename)
		(fatalError, blocks) = parseTeXLogFile(filename)
		errmsg = extractErrorMessageFromTeXLogs(filename, fatalError, blocks, False, '')
		self.assertEqual('./documentation.tex:209: Undefined control sequence.\\beamer@doifinframe ... text on the slides. \\refa{noref} \\end {itemize} \\en...l.209 \\end{frame}', errmsg)

	def test_extractErrorMessageFromTeXLogs_noFatal_extension(self):
		filename = genutils.findFileInPath("test1.txt")
		self.assertIsNotNone(filename)
		(fatalError, blocks) = parseTeXLogFile(filename)
		errmsg = extractErrorMessageFromTeXLogs(filename, fatalError, blocks, True, '')
		self.assertEqual('', errmsg)

	def test_extractErrorMessageFromTeXLogs_fatal_extension(self):
		filename = genutils.findFileInPath("test2.txt")
		self.assertIsNotNone(filename)
		(fatalError, blocks) = parseTeXLogFile(filename)
		errmsg = extractErrorMessageFromTeXLogs(filename, fatalError, blocks, True, '')
		self.assertEqual('./documentation.tex:209: Undefined control sequence.\\beamer@doifinframe ... text on the slides. \\refa{noref} \\end {itemize} \\en...l.209 \\end{frame}', errmsg)



if __name__ == '__main__':
    unittest.main()

