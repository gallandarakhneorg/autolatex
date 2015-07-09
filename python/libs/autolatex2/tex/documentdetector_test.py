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
import tempfile
import os
import logging

from autolatex2.tex import documentdetector
from autolatex2.utils import debug

class TestDocumentDetectorFromString(unittest.TestCase):

	def setUp(self):
		logging.getLogger().setLevel(logging.CRITICAL)

	def __run(self, content : str) -> bool:
		detector = documentdetector.DocumentDetector(None, content)
		detector.run()
		return detector.latex

	def test_emptyString(self):
		self.assertFalse(self.__run(''))

	def test_noLaTeX(self):
		self.assertFalse(self.__run('abc'))

	def test_atBegining(self):
		self.assertTrue(self.__run(r'\documentclass{article}\begin{document}\end{document}'))

	def test_withComment1(self):
		self.assertFalse(self.__run(r'%Mycomment\documentclass{article}\begin{document}\end{document}'))

	def test_withComment2(self):
		self.assertTrue(self.__run(r'%Mycomment' + "\n" + r'\documentclass{article}\begin{document}\end{document}'))

	def test_withMath1(self):
		self.assertTrue(self.__run(r'\begin{document}$A_1$\end{document}\documentclass{article}'))

	def test_withMath2(self):
		self.assertTrue(self.__run(r'\begin{document}\[A_1\]\end{document}\documentclass{article}'))


class TestDocumentDetectorFromFile(unittest.TestCase):

	def setUp(self):
		logging.getLogger().setLevel(logging.CRITICAL)

	def __run(self, expected : bool, content : str):
		f = tempfile.NamedTemporaryFile(delete=False)
		name = f.name
		f.file.write(bytes(content, 'UTF-8'))
		f.seek(0)
		f.close
		detector = documentdetector.DocumentDetector(name)
		detector.run()
		is_latex = detector.latex
		os.remove(name)
		if expected:
			self.assertTrue(is_latex)
		else:
			self.assertFalse(is_latex)

	def test_emptyFile(self):
		self.__run(False, "\n")

	def test_noLaTeX(self):
		self.__run(False, "abc")

	def test_atBegining(self):
		self.__run(True, r'\documentclass{article}\begin{document}\end{document}')

	def test_withComment1(self):
		self.__run(False, r'%Mycomment\documentclass{article}\begin{document}\end{document}')

	def test_withComment2(self):
		self.__run(True, r'%Mycomment' + "\n" + r'\documentclass{article}\begin{document}\end{document}')

	def test_withMath(self):
		self.__run(True, r'\begin{document}$A_1$\end{document}\documentclass{article}')

	def test_withMath2(self):
		self.__run(True, r'\begin{document}\[A_1\]\end{document}\documentclass{article}')



if __name__ == '__main__':
    unittest.main()

