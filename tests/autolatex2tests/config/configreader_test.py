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
import os

from autolatex2.config import configreader
from autolatex2.config.configobj import Config
from autolatex2.config.translator import TranslatorLevel

class TestOldStyleConfigReader(unittest.TestCase):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.__config = None
		self.__filename = None
		self.__reader = None
		self.__cfg = None
		self._dir = None

	def setUp(self):
		logging.getLogger().setLevel(logging.CRITICAL)
		self.__config = Config()
		self._dir = os.path.normpath(os.path.join(os.path.dirname(__file__),  '..', 'dev-resources'))
		self.__filename = os.path.join(self._dir,  'config.ini')
		self.__reader = configreader.OldStyleConfigReader()
		self.__cfg = self.__reader.read(self.__filename,  TranslatorLevel.USER)
		self.assertIsNotNone(self.__cfg)

	@property
	def rconfig(self) -> Config:
		return self.__cfg

	def test_generation_generateimages(self):
		self.assertTrue(self.rconfig.translators.is_translator_enable)

	def test_generation_imagedirectory(self):
		self.assertEqual([os.path.join(self._dir, 'a', 'b', 'c', 'd'),
			os.path.join(self._dir, 'x', 'y', 'z')], self.rconfig.translators.imagePaths)

	def test_generation_generationtype(self):
		self.assertFalse(self.rconfig.generation.pdfMode)

	def test_generation_texcompiler(self):
		self.assertEqual('xelatex',  self.rconfig.generation.latexCompiler)

	def test_generation_synctex(self):
		self.assertTrue(self.rconfig.generation.synctex)

	def test_generation_tranlatorincludepath(self):
		actual = self.rconfig.translators.includePaths
		self.assertEqual([os.path.join(self._dir, 'path1'),
			os.path.join(self._dir, 'path2', 'a')],  actual)

	def test_generation_latexcmd(self):
		self.assertEqual(['latex2'],  self.rconfig.generation.latexCLI)

	def test_generation_bibtexcmd(self):
		self.assertEqual(['bibtex2'],  self.rconfig.generation.bibtexCLI)

	def test_generation_bibercmd(self):
		self.assertEqual(['biber2'],  self.rconfig.generation.biberCLI)

	def test_generation_makeglossariescmd(self):
		self.assertEqual(['mkg'],  self.rconfig.generation.makeglossaryCLI)

	def test_generation_makeindexcmd(self):
		self.assertEqual(['mkidx'],  self.rconfig.generation.makeindexCLI)

	def test_generation_dvi2pscmd(self):
		self.assertEqual(['dvips2'],  self.rconfig.generation.dvipsCLI)

	def test_generation_latexflags(self):
		self.assertEqual(['-f1',  '-f2'],  self.rconfig.generation.latexFlags)

	def test_generation_bibtexflags(self):
		self.assertEqual(['-f3',  '-f4'],  self.rconfig.generation.bibtexFlags)

	def test_generation_biberflags(self):
		self.assertEqual(['-f5',  '-f6'],  self.rconfig.generation.biberFlags)

	def test_generation_makegossariesflags(self):
		self.assertEqual(['-f7',  '-f8'],  self.rconfig.generation.makeglossaryFlags)

	def test_generation_makeindexflags(self):
		self.assertEqual(['-f9',  '-f10'],  self.rconfig.generation.makeindexFlags)

	def test_generation_dvi2psflags(self):
		self.assertEqual(['-f11',  '-f12'],  self.rconfig.generation.dvipsFlags)

	def test_generation_mainfile(self):
		absdir = os.path.dirname(os.path.normpath(os.path.join(self._dir,  os.path.join('.',  'a',  't.tex'))))
		self.assertEqual(absdir,  self.rconfig.documentDirectory)
		self.assertEqual('t.tex',  self.rconfig.documentFilename)

	def test_generation_makeindexstyle(self):
		self.assertEqual(os.path.join(self.__config.installationDirectory,  'default.ist'),  self.rconfig.generation.makeindexStyleFilename)




if __name__ == '__main__':
    unittest.main()

