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
import os
import time

from pathlib import Path

from autolatex2.utils.extlogging import ensureAutoLaTeXLoggingLevels
from autolatex2.make.maketool import *
from autolatex2.translator.translatorobj import *
from autolatex2.config.configobj import *
from autolatex2.tex.utils import TeXWarnings
import autolatex2.utils.utilfunctions as genutils

class TestInitAutoLaTeXMaker(unittest.TestCase):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.config = None
		self.repo = None
		self.runner = None

	def setUp(self):
		logging.getLogger().setLevel(logging.CRITICAL)
		self.config = Config()
		self.config.translators.ignoreSystemTranslators = True
		self.config.translators.ignoreUserTranslators = True
		self.config.translators.ignoreDocumentTranslators = True
		self.config.translators.includePaths = []
		self.config.translators.imagePaths = []
		self.config.translators.imagePaths = []
		self.repo = TranslatorRepository(self.config)
		self.runner = TranslatorRunner(self.repo)

	def test_default_compilerDefinition(self):
		maker = AutoLaTeXMaker(self.runner)
		cd = maker.compilerDefinition
		self.assertIsNotNone(cd)
		self.assertEqual('pdflatex', cd['cmd'])

	def test_pdflatex_compilerDefinition(self):
		self.config.generation.latexCompiler = 'pdflatex'
		maker = AutoLaTeXMaker(self.runner)
		cd = maker.compilerDefinition
		self.assertIsNotNone(cd)
		self.assertEqual('pdflatex', cd['cmd'])

	def test_latex_compilerDefinition(self):
		self.config.generation.latexCompiler = 'latex'
		maker = AutoLaTeXMaker(self.runner)
		cd = maker.compilerDefinition
		self.assertIsNotNone(cd)
		self.assertEqual('latex', cd['cmd'])

	def test_existingLatexCLI_noFlag(self):
		self.config.generation.latexCLI = ['a', 'b', 'c']
		maker = AutoLaTeXMaker(self.runner)
		cli = maker.latexCLI
		self.assertIsNotNone(cli)
		self.assertEqual(['a', 'b', 'c'], cli)

	def test_existingLatexCLI_flags(self):
		self.config.generation.latexCLI = ['a', 'b', 'c']
		self.config.generation.latexFlags = ['d', 'e', 'f']
		maker = AutoLaTeXMaker(self.runner)
		cli = maker.latexCLI
		self.assertIsNotNone(cli)
		self.assertEqual(['a', 'b', 'c', 'd', 'e', 'f'], cli)

	def test_pdflatexCli_noFlag_pdfMode(self):
		maker = AutoLaTeXMaker(self.runner)
		cli = maker.latexCLI
		self.assertIsNotNone(cli)
		self.assertEqual(['pdflatex', '-halt-on-error', '-interaction', 'batchmode', '-file-line-error', '-output-format=pdf'], cli)

	def test_pdflatexCLI_flags_pdfMode(self):
		self.config.generation.latexFlags = ['d', 'e', 'f']
		maker = AutoLaTeXMaker(self.runner)
		cli = maker.latexCLI
		self.assertIsNotNone(cli)
		self.assertEqual(['pdflatex', '-halt-on-error', '-interaction', 'batchmode', '-file-line-error', '-output-format=pdf', 'd', 'e', 'f'], cli)

	def test_pdflatexCli_noFlag_psMode(self):
		self.config.generation.pdfMode = False
		maker = AutoLaTeXMaker(self.runner)
		cli = maker.latexCLI
		self.assertIsNotNone(cli)
		self.assertEqual(['latex', '-halt-on-error', '-interaction', 'batchmode', '-file-line-error', '-output-format=dvi'], cli)

	def test_pdflatexCLI_flags_psMode(self):
		self.config.generation.pdfMode = False
		self.config.generation.latexFlags = ['d', 'e', 'f']
		maker = AutoLaTeXMaker(self.runner)
		cli = maker.latexCLI
		self.assertIsNotNone(cli)
		self.assertEqual(['latex', '-halt-on-error', '-interaction', 'batchmode', '-file-line-error', '-output-format=dvi', 'd', 'e', 'f'], cli)

	def test_pdflatexCli_noFlag_pdfMode_synctex(self):
		self.config.generation.synctex = True
		maker = AutoLaTeXMaker(self.runner)
		cli = maker.latexCLI
		self.assertIsNotNone(cli)
		self.assertEqual(['pdflatex', '-halt-on-error', '-interaction', 'batchmode', '-file-line-error', '-synctex=1', '-output-format=pdf'], cli)

	def test_pdflatexCLI_flags_pdfMode_synctex(self):
		self.config.generation.synctex = True
		self.config.generation.latexFlags = ['d', 'e', 'f']
		maker = AutoLaTeXMaker(self.runner)
		cli = maker.latexCLI
		self.assertIsNotNone(cli)
		self.assertEqual(['pdflatex', '-halt-on-error', '-interaction', 'batchmode', '-file-line-error', '-synctex=1', '-output-format=pdf', 'd', 'e', 'f'], cli)

	def test_pdflatexCli_noFlag_psMode_synctex(self):
		self.config.generation.synctex = True
		self.config.generation.pdfMode = False
		maker = AutoLaTeXMaker(self.runner)
		cli = maker.latexCLI
		self.assertIsNotNone(cli)
		self.assertEqual(['latex', '-halt-on-error', '-interaction', 'batchmode', '-file-line-error', '-synctex=1', '-output-format=dvi'], cli)

	def test_pdflatexCLI_flags_psMode_synctex(self):
		self.config.generation.synctex = True
		self.config.generation.pdfMode = False
		self.config.generation.latexFlags = ['d', 'e', 'f']
		maker = AutoLaTeXMaker(self.runner)
		cli = maker.latexCLI
		self.assertIsNotNone(cli)
		self.assertEqual(['latex', '-halt-on-error', '-interaction', 'batchmode', '-file-line-error', '-synctex=1', '-output-format=dvi', 'd', 'e', 'f'], cli)

	def test_existingBibtexCLI(self):
		self.config.generation.bibtexCLI = ['a', 'b', 'c']
		maker = AutoLaTeXMaker(self.runner)
		cli = maker.bibtexCLI
		self.assertIsNotNone(cli)
		self.assertEqual(['a', 'b', 'c'], cli)

	def test_bibtexCLI_noFlag(self):
		maker = AutoLaTeXMaker(self.runner)
		cli = maker.bibtexCLI
		self.assertIsNotNone(cli)
		self.assertEqual(['bibtex'], cli)

	def test_bibtexCLI_flags(self):
		self.config.generation.bibtexFlags = ['d', 'e', 'f']
		maker = AutoLaTeXMaker(self.runner)
		cli = maker.bibtexCLI
		self.assertIsNotNone(cli)
		self.assertEqual(['bibtex', 'd', 'e', 'f'], cli)

	def test_existingBiberCLI(self):
		self.config.generation.biberCLI = ['a', 'b', 'c']
		maker = AutoLaTeXMaker(self.runner)
		cli = maker.biberCLI
		self.assertIsNotNone(cli)
		self.assertEqual(['a', 'b', 'c'], cli)

	def test_biberCLI_noFlag(self):
		maker = AutoLaTeXMaker(self.runner)
		cli = maker.biberCLI
		self.assertIsNotNone(cli)
		self.assertEqual(['biber'], cli)

	def test_biberCLI_flags(self):
		self.config.generation.biberFlags = ['d', 'e', 'f']
		maker = AutoLaTeXMaker(self.runner)
		cli = maker.biberCLI
		self.assertIsNotNone(cli)
		self.assertEqual(['biber', 'd', 'e', 'f'], cli)

	def test_existingMakeindexCLI(self):
		self.config.generation.makeindexCLI = ['a', 'b', 'c']
		maker = AutoLaTeXMaker(self.runner)
		cli = maker.makeindexCLI
		self.assertIsNotNone(cli)
		self.assertEqual(['a', 'b', 'c'], cli)

	def test_makeindexCLI_noFlag(self):
		maker = AutoLaTeXMaker(self.runner)
		cli = maker.makeindexCLI
		self.assertIsNotNone(cli)
		self.assertEqual(['makeindex'], cli)

	def test_makeindexCLI_flags(self):
		self.config.generation.makeindexFlags = ['d', 'e', 'f']
		maker = AutoLaTeXMaker(self.runner)
		cli = maker.makeindexCLI
		self.assertIsNotNone(cli)
		self.assertEqual(['makeindex', 'd', 'e', 'f'], cli)

	def test_existingMakeglossariesCLI(self):
		self.config.generation.makeglossaryCLI = ['a', 'b', 'c']
		maker = AutoLaTeXMaker(self.runner)
		cli = maker.makeglossariesCLI
		self.assertIsNotNone(cli)
		self.assertEqual(['a', 'b', 'c'], cli)

	def test_makeglossariesCLI_noFlag(self):
		maker = AutoLaTeXMaker(self.runner)
		cli = maker.makeglossariesCLI
		self.assertIsNotNone(cli)
		self.assertEqual(['makeglossaries'], cli)

	def test_makeglossariesCLI_flags(self):
		self.config.generation.makeglossaryFlags = ['d', 'e', 'f']
		maker = AutoLaTeXMaker(self.runner)
		cli = maker.makeglossariesCLI
		self.assertIsNotNone(cli)
		self.assertEqual(['makeglossaries', 'd', 'e', 'f'], cli)

	def test_existingDvipsCLI(self):
		self.config.generation.dvipsCLI = ['a', 'b', 'c']
		maker = AutoLaTeXMaker(self.runner)
		cli = maker.dvipsCLI
		self.assertIsNotNone(cli)
		self.assertEqual(['a', 'b', 'c'], cli)

	def test_dvipsCLI_noFlag(self):
		maker = AutoLaTeXMaker(self.runner)
		cli = maker.dvipsCLI
		self.assertIsNotNone(cli)
		self.assertEqual(['dvips'], cli)

	def test_dvipsCLI_flags(self):
		self.config.generation.dvipsFlags = ['d', 'e', 'f']
		maker = AutoLaTeXMaker(self.runner)
		cli = maker.dvipsCLI
		self.assertIsNotNone(cli)
		self.assertEqual(['dvips', 'd', 'e', 'f'], cli)

	def test_pdflatex_extendedWarnings(self):
		self.config.generation.latexCompiler = 'pdflatex'
		self.config.generation.extendedWarnings = True
		maker = AutoLaTeXMaker(self.runner)
		self.assertTrue(maker.extendedWarningsEnabled)
		self.assertNotEqual('', maker.extendedWarningsCode)

	def test_lualatex_extendedWarnings(self):
		self.config.generation.latexCompiler = 'lualatex'
		self.config.generation.extendedWarnings = True
		maker = AutoLaTeXMaker(self.runner)
		self.assertTrue(maker.extendedWarningsEnabled)
		self.assertNotEqual('', maker.extendedWarningsCode)

	def test_latex_extendedWarnings(self):
		self.config.generation.latexCompiler = 'latex'
		self.config.generation.extendedWarnings = True
		maker = AutoLaTeXMaker(self.runner)
		self.assertTrue(maker.extendedWarningsEnabled)
		self.assertNotEqual('', maker.extendedWarningsCode)


class TestPrivateFunctionsAutoLaTeXMaker(unittest.TestCase):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.config = None
		self.repo = None
		self.runner = None
		self.__maker = None

	def setUp(self):
		logging.getLogger().setLevel(logging.CRITICAL)
		self.config = Config()
		self.config.translators.ignoreSystemTranslators = True
		self.config.translators.ignoreUserTranslators = True
		self.config.translators.ignoreDocumentTranslators = True
		self.config.translators.includePaths = []
		self.config.translators.imagePaths = []
		self.repo = TranslatorRepository(self.config)
		self.runner = TranslatorRunner(self.repo)
		self.__maker = AutoLaTeXMaker(self.runner)

	@property
	def maker(self):
		return self.__maker

	def test___testLaTeXWarningOn_01(self):
		pass



class TestAutoLaTeXMaker(unittest.TestCase):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.config = None
		self.repo = None
		self.runner = None
		self.__maker = None

	def setUp(self):
		ensureAutoLaTeXLoggingLevels()
		logging.getLogger().setLevel(logging.CRITICAL)
		self.config = Config()
		self.config.translators.ignoreSystemTranslators = True
		self.config.translators.ignoreUserTranslators = True
		self.config.translators.ignoreDocumentTranslators = True
		self.config.translators.includePaths = []
		#
		self.dev_ressources_dir = os.path.join(self.config.installationDirectory,  'python', 'autolatex2', 'dev-resources')
		self.config.documentDirectory = self.dev_ressources_dir
		#
		img_dir = os.path.join(self.dev_ressources_dir, 'images')
		self.config.translators.imagePaths = [ img_dir ]
		#
		self.repo = TranslatorRepository(self.config)
		self.runner = TranslatorRunner(self.repo)

	def tearDown(self):
		self.config = None
		self.repo = None
		self.runner = None
		self.__maker = None

	@property
	def maker(self):
		if self.__maker is None:
			self.__maker = AutoLaTeXMaker(self.runner)
		return self.__maker

	def assertIsFile(self,  filename : str):
		self.assertTrue(os.path.isfile(filename))

	def assertDependency(self,  dependencies : dict,  filename : str,  type : str,  deps : set):
		self.assertTrue(filename in dependencies)
		self.assertIsNotNone(dependencies[filename])
		desc = dependencies[filename]
		self.assertEqual(type,  desc.fileType)
		self.assertEqual(deps,  desc.dependencies)
	
	def __cleanTmpLatexFile(self, name : str):
		fn = genutils.basename2(name, ".tex")+".log"
		genutils.unlink(fn)
		fn = genutils.basename2(name, ".tex")+".aux"
		genutils.unlink(fn)
		fn = genutils.basename2(name, ".tex")+".bbl"
		genutils.unlink(fn)
		fn = genutils.basename2(name, ".tex")+".blg"
		genutils.unlink(fn)
		fn = genutils.basename2(name, ".tex")+".pdf"
		genutils.unlink(fn)
		fn = genutils.basename2(name, ".tex")+".bcf"
		genutils.unlink(fn)
		fn = genutils.basename2(name, ".tex")+".run.xml"
		genutils.unlink(fn)
		fn = genutils.basename2(name, ".tex")+".idx"
		genutils.unlink(fn)
		fn = genutils.basename2(name, ".tex")+".ind"
		genutils.unlink(fn)
		fn = genutils.basename2(name, ".tex")+".ilg"
		genutils.unlink(fn)
		fn = genutils.basename2(name, ".tex")+".glo"
		genutils.unlink(fn)
		fn = genutils.basename2(name, ".tex")+".gls"
		genutils.unlink(fn)
		fn = genutils.basename2(name, ".tex")+".dvi"
		genutils.unlink(fn)
		fn = genutils.basename2(name, ".tex")+".ps"
		genutils.unlink(fn)

	def __cleanTmpFigureFile(self, paths : list):
		for path in paths:
			fn = os.path.join(path,  'english.png')
			genutils.unlink(fn)
			fn = os.path.join(path,  'subfolder', 'french.png')
			genutils.unlink(fn)

	##################################################################################"

	def test_reset(self):
		self.maker.reset()
		self.assertEqual(0, len(self.maker.files))
		self.assertEqual(0, len(self.maker.standardWarnings))
		self.assertEqual(0, len(self.maker.extendedWarnings))
		self.assertEqual(0, len(self.maker.rootFiles))

	def test_rootFiles(self):
		self.assertEqual(0, len(self.maker.rootFiles))

	def test_addRootFile(self):
		self.maker.addRootFile('a/b/c')
		self.assertEqual(1, len(self.maker.rootFiles))
		self.assertEqual({'a/b/c'},  self.maker.rootFiles)

	def test_files(self):
		self.assertEqual(0, len(self.maker.files))

	def test_standardWarnings(self):
		self.assertEqual(0, len(self.maker.standardWarnings))

	def test_extendedWarnings(self):
		self.assertEqual(0, len(self.maker.extendedWarnings))

	def test_run_latex_1a(self):
		texfile = genutils.findFileInPath("test1.tex")
		self.assertIsNotNone(texfile)
		self.__cleanTmpLatexFile(texfile)
		try:
			nb = self.maker.run_latex(texfile, False)
			self.assertEqual(1, nb)
			self.assertEqual(0, len(self.maker.standardWarnings))
			self.assertEqual(0, len(self.maker.extendedWarnings))
		finally:
			self.__cleanTmpLatexFile(texfile)

	def test_run_latex_1b(self):
		texfile = genutils.findFileInPath("test1.tex")
		self.assertIsNotNone(texfile)
		self.__cleanTmpLatexFile(texfile)
		try:
			nb = self.maker.run_latex(texfile, True)
			self.assertEqual(1, nb)
			self.assertEqual(0, len(self.maker.standardWarnings))
			self.assertEqual(0, len(self.maker.extendedWarnings))
		finally:
			self.__cleanTmpLatexFile(texfile)

	def test_run_latex_2a(self):
		texfile = genutils.findFileInPath("test2.tex")
		self.assertIsNotNone(texfile)
		self.__cleanTmpLatexFile(texfile)
		try:
			nb = self.maker.run_latex(texfile, False)
			self.assertEqual(1, nb)
			self.assertEqual(1, len(self.maker.standardWarnings))
			self.assertEqual(2, len(self.maker.extendedWarnings))
			self.assertEqual(set([TeXWarnings.undefined_reference]),  self.maker.standardWarnings)
		finally:
			self.__cleanTmpLatexFile(texfile)

	def test_run_latex_2b(self):
		texfile = genutils.findFileInPath("test2.tex")
		self.assertIsNotNone(texfile)
		self.__cleanTmpLatexFile(texfile)
		try:
			nb = self.maker.run_latex(texfile, True)
			self.assertEqual(1, nb)
			self.assertEqual(1, len(self.maker.standardWarnings))
			self.assertEqual(2, len(self.maker.extendedWarnings))
			self.assertEqual(set([TeXWarnings.undefined_reference]),  self.maker.standardWarnings)
		finally:
			self.__cleanTmpLatexFile(texfile)

	def test_run_latex_3a(self):
		texfile = genutils.findFileInPath("test3.tex")
		self.assertIsNotNone(texfile)
		self.__cleanTmpLatexFile(texfile)
		try:
			nb = self.maker.run_latex(texfile, False)
			self.assertEqual(1, nb)
			self.assertEqual(1, len(self.maker.standardWarnings))
			self.assertEqual(4, len(self.maker.extendedWarnings))
			self.assertEqual(set([TeXWarnings.undefined_reference]),  self.maker.standardWarnings)
		finally:
			self.__cleanTmpLatexFile(texfile)

	def test_run_latex_3b(self):
		texfile = genutils.findFileInPath("test3.tex")
		self.assertIsNotNone(texfile)
		self.__cleanTmpLatexFile(texfile)
		try:
			nb = self.maker.run_latex(texfile, True)
			self.assertEqual(2, nb)
			self.assertEqual(0, len(self.maker.standardWarnings))
			self.assertEqual(0, len(self.maker.extendedWarnings))
		finally:
			self.__cleanTmpLatexFile(texfile)

	def test_run_latex_4a(self):
		texfile = genutils.findFileInPath("test4.tex")
		self.assertIsNotNone(texfile)
		self.__cleanTmpLatexFile(texfile)
		try:
			nb = self.maker.run_latex(texfile, False)
			self.assertEqual(1, nb)
			self.assertEqual(1, len(self.maker.standardWarnings))
			self.assertEqual(4, len(self.maker.extendedWarnings))
			self.assertEqual(set([TeXWarnings.undefined_reference]),  self.maker.standardWarnings)
		finally:
			self.__cleanTmpLatexFile(texfile)

	def test_run_latex_4b(self):
		texfile = genutils.findFileInPath("test4.tex")
		self.assertIsNotNone(texfile)
		self.__cleanTmpLatexFile(texfile)
		try:
			nb = self.maker.run_latex(texfile, True)
			self.assertEqual(2, nb)
			self.assertEqual(1, len(self.maker.standardWarnings))
			self.assertEqual(2, len(self.maker.extendedWarnings))
			self.assertEqual(set([TeXWarnings.undefined_reference]),  self.maker.standardWarnings)
		finally:
			self.__cleanTmpLatexFile(texfile)

	def test_run_latex_5a(self):
		texfile = genutils.findFileInPath("test5.tex")
		self.assertIsNotNone(texfile)
		self.__cleanTmpLatexFile(texfile)
		try:
			nb = self.maker.run_latex(texfile, False)
			self.assertEqual(1, nb)
			self.assertEqual(2, len(self.maker.standardWarnings))
			self.assertEqual(2, len(self.maker.extendedWarnings))
			self.assertEqual(set([TeXWarnings.undefined_reference,  TeXWarnings.undefined_citation]),  self.maker.standardWarnings)
		finally:
			self.__cleanTmpLatexFile(texfile)

	def test_run_latex_5b(self):
		texfile = genutils.findFileInPath("test5.tex")
		self.assertIsNotNone(texfile)
		self.__cleanTmpLatexFile(texfile)
		try:
			nb = self.maker.run_latex(texfile, True)
			self.assertEqual(1, nb)
			self.assertEqual(2, len(self.maker.standardWarnings))
			self.assertEqual(2, len(self.maker.extendedWarnings))
			self.assertEqual(set([TeXWarnings.undefined_reference,  TeXWarnings.undefined_citation]),  self.maker.standardWarnings)
		finally:
			self.__cleanTmpLatexFile(texfile)

	def test_run_latex_6a(self):
		texfile = genutils.findFileInPath("test6.tex")
		self.assertIsNotNone(texfile)
		self.__cleanTmpLatexFile(texfile)
		try:
			nb = self.maker.run_latex(texfile, False)
			self.assertEqual(1, nb)
			self.assertEqual(2, len(self.maker.standardWarnings))
			self.assertEqual(2, len(self.maker.extendedWarnings))
			self.assertEqual(set([TeXWarnings.undefined_reference,  TeXWarnings.undefined_citation]),  self.maker.standardWarnings)
		finally:
			self.__cleanTmpLatexFile(texfile)

	def test_run_latex_6b(self):
		texfile = genutils.findFileInPath("test6.tex")
		self.assertIsNotNone(texfile)
		self.__cleanTmpLatexFile(texfile)
		try:
			nb = self.maker.run_latex(texfile, True)
			self.assertEqual(1, nb)
			self.assertEqual(2, len(self.maker.standardWarnings))
			self.assertEqual(2, len(self.maker.extendedWarnings))
			self.assertEqual(set([TeXWarnings.undefined_reference,  TeXWarnings.undefined_citation]),  self.maker.standardWarnings)
		finally:
			self.__cleanTmpLatexFile(texfile)

	def test_run_latex_7a(self):
		texfile = genutils.findFileInPath("test7.tex")
		self.assertIsNotNone(texfile)
		self.__cleanTmpLatexFile(texfile)
		try:
			nb = self.maker.run_latex(texfile, False)
			self.assertEqual(1, nb)
			self.assertEqual(2, len(self.maker.standardWarnings))
			self.assertEqual(2, len(self.maker.extendedWarnings))
			self.assertEqual(set([TeXWarnings.undefined_reference,  TeXWarnings.undefined_citation]),  self.maker.standardWarnings)
		finally:
			self.__cleanTmpLatexFile(texfile)

	def test_run_latex_7b(self):
		texfile = genutils.findFileInPath("test7.tex")
		self.assertIsNotNone(texfile)
		self.__cleanTmpLatexFile(texfile)
		try:
			nb = self.maker.run_latex(texfile, True)
			self.assertEqual(1, nb)
			self.assertEqual(2, len(self.maker.standardWarnings))
			self.assertEqual(2, len(self.maker.extendedWarnings))
			self.assertEqual(set([TeXWarnings.undefined_reference,  TeXWarnings.undefined_citation]),  self.maker.standardWarnings)
		finally:
			self.__cleanTmpLatexFile(texfile)

	def test_run_bibtex_5(self):
		texfile = genutils.findFileInPath("test5.tex")
		self.assertIsNotNone(texfile)
		bibfile = genutils.findFileInPath("test5.bib")
		self.assertIsNotNone(bibfile)
		bibfile = os.path.relpath(bibfile)
		self.assertEqual(os.path.join('autolatex2',  'dev-resources',  'test5.bib'),  bibfile)
		self.__cleanTmpLatexFile(texfile)
		try:
			# Run LaTeX tool prior to the BibTeX tool
			self.maker.run_latex(texfile,  False)
			# Run BibTeX
			error = self.maker.run_bibtex(texfile)
			self.assertIsNone(error)
			self.assertEqual(0, len(self.maker.standardWarnings))
			self.assertEqual(0, len(self.maker.extendedWarnings))
		finally:
			self.__cleanTmpLatexFile(texfile)

	def test_run_bibtex_6(self):
		texfile = genutils.findFileInPath("test6.tex")
		self.assertIsNotNone(texfile)
		bibfile = genutils.findFileInPath("test5.bib")
		self.assertIsNotNone(bibfile)
		bibfile = os.path.relpath(bibfile)
		self.assertEqual(os.path.join('autolatex2',  'dev-resources',  'test5.bib'),  bibfile)
		self.__cleanTmpLatexFile(texfile)
		try:
			# Run LaTeX tool prior to the BibTeX tool
			self.maker.run_latex(texfile,  False)
			# Run BibTeX
			error = self.maker.run_bibtex(texfile)
			self.assertIsNone(error)
			self.assertEqual(0, len(self.maker.standardWarnings))
			self.assertEqual(0, len(self.maker.extendedWarnings))
		finally:
			self.__cleanTmpLatexFile(texfile)

	def test_run_bibtex_7(self):
		texfile = genutils.findFileInPath("test7.tex")
		self.assertIsNotNone(texfile)
		bibfile = genutils.findFileInPath("test7.bib")
		self.assertIsNotNone(bibfile)
		bibfile = os.path.relpath(bibfile)
		self.assertEqual(os.path.join('autolatex2',  'dev-resources',  'test7.bib'),  bibfile)
		self.__cleanTmpLatexFile(texfile)
		try:
			# Run LaTeX tool prior to the BibTeX tool
			self.maker.run_latex(texfile,  False)
			# Run BibTeX
			error = self.maker.run_bibtex(texfile)
			self.assertIsNotNone(error)
			self.assertEqual(os.path.join('autolatex2', 'dev-resources',  'test7.bib'), error['filename'])
			self.assertEqual(8,  error['lineno'])
			self.assertEqual('I was expecting a `,\' or a `}\'  year = 2021',  error['message'])
			self.assertEqual(0, len(self.maker.standardWarnings))
			self.assertEqual(0, len(self.maker.extendedWarnings))
		finally:
			self.__cleanTmpLatexFile(texfile)

	def test_runBiber_8(self):
		texfile = genutils.findFileInPath("test8.tex")
		self.assertIsNotNone(texfile)
		bibfile = genutils.findFileInPath("test5.bib")
		self.assertIsNotNone(bibfile)
		bibfile = os.path.relpath(bibfile)
		self.assertEqual(os.path.join('autolatex2',  'dev-resources',  'test5.bib'),  bibfile)
		self.__cleanTmpLatexFile(texfile)
		# Force Biber use
		self.maker.configuration.generation.is_biber = True
		try:
			# Run LaTeX tool prior to the Biber tool
			self.maker.run_latex(texfile,  False)
			# Run Biber
			error = self.maker.run_bibtex(texfile)
			self.assertIsNone(error)
			self.assertEqual(0, len(self.maker.standardWarnings))
			self.assertEqual(0, len(self.maker.extendedWarnings))
		finally:
			self.__cleanTmpLatexFile(texfile)

	def test_run_bibtex_9(self):
		texfile = genutils.findFileInPath("test9.tex")
		self.assertIsNotNone(texfile)
		bibfile = genutils.findFileInPath("test5.bib")
		self.assertIsNotNone(bibfile)
		bibfile = os.path.relpath(bibfile)
		self.assertEqual(os.path.join('autolatex2',  'dev-resources',  'test5.bib'),  bibfile)
		self.__cleanTmpLatexFile(texfile)
		# Force Biber use
		self.maker.configuration.generation.is_biber = True
		try:
			# Run LaTeX tool prior to the Biber tool
			self.maker.run_latex(texfile,  False)
			# Run Biber
			error = self.maker.run_bibtex(texfile)
			self.assertIsNone(error)
			self.assertEqual(0, len(self.maker.standardWarnings))
			self.assertEqual(0, len(self.maker.extendedWarnings))
		finally:
			self.__cleanTmpLatexFile(texfile)

	def test_run_bibtex_10(self):
		texfile = genutils.findFileInPath("test10.tex")
		self.assertIsNotNone(texfile)
		bibfile = genutils.findFileInPath("test7.bib")
		self.assertIsNotNone(bibfile)
		bibfile = os.path.relpath(bibfile)
		self.assertEqual(os.path.join('autolatex2',  'dev-resources',  'test7.bib'),  bibfile)
		self.__cleanTmpLatexFile(texfile)
		# Force Biber use
		self.maker.configuration.generation.is_biber = True
		try:
			# Run LaTeX tool prior to the BibTeX tool
			self.maker.run_latex(texfile,  False)
			# Run BibTeX
			error = self.maker.run_bibtex(texfile)
			self.assertIsNotNone(error)
			self.assertEqual('test7.bib', os.path.basename(error['filename']))
			self.assertEqual(8,  error['lineno'])
			self.assertEqual('syntax error: found "year", expected end of entry ("}" or ")") (skipping to next "@")',  error['message'])
			self.assertEqual(0, len(self.maker.standardWarnings))
			self.assertEqual(0, len(self.maker.extendedWarnings))
		finally:
			self.__cleanTmpLatexFile(texfile)

	def test_run_makeindex_11(self):
		texfile = genutils.findFileInPath("test11.tex")
		self.assertIsNotNone(texfile)
		idxfile = genutils.basename2(texfile,  '.tex') + '.idx'
		self.assertIsNotNone(idxfile)
		self.__cleanTmpLatexFile(texfile)
		try:
			# Run LaTeX tool prior to the MakeIndex tool
			self.maker.run_latex(texfile,  False)
			# Run MakeIndex
			success = self.maker.run_makeindex(idxfile)
			self.assertTrue(success)
			self.assertEqual(0, len(self.maker.standardWarnings))
			self.assertEqual(0, len(self.maker.extendedWarnings))
		finally:
			self.__cleanTmpLatexFile(texfile)

	def test_run_makeindex_12(self):
		texfile = genutils.findFileInPath("test11.tex")
		self.assertIsNotNone(texfile)
		idxfile = genutils.basename2(texfile,  '.tex') + '.idx'
		self.assertIsNotNone(idxfile)
		istfile = genutils.basename2(texfile,  '.tex') + '.ist'
		self.assertIsNotNone(istfile)
		self.__cleanTmpLatexFile(texfile)
		# Force IST-file use
		self.maker.configuration.generation.makeindexStyleFilename = istfile
		try:
			# Run LaTeX tool prior to the MakeIndex tool
			self.maker.run_latex(texfile,  False)
			# Run MakeIndex
			success = self.maker.run_makeindex(idxfile)
			self.assertTrue(success)
			self.assertEqual(0, len(self.maker.standardWarnings))
			self.assertEqual(0, len(self.maker.extendedWarnings))
		finally:
			self.__cleanTmpLatexFile(texfile)

	def test_compute_dependencies_1(self):
		texfile = genutils.findFileInPath("test1.tex")
		pdffile = os.path.join(os.path.dirname(texfile),  'test1.pdf')
		self.assertIsNotNone(texfile)
		self.__cleanTmpLatexFile(texfile)
		root_dep_file,  deps = self.maker.compute_dependencies(texfile,  False)
		self.assertEquals(pdffile,  root_dep_file)
		self.assertIsNotNone(deps)
		self.assertDependency(deps, texfile,  'tex',  set())

	def test_compute_dependencies_8(self):
		texfile = genutils.findFileInPath("test8.tex")
		pdffile = os.path.join(os.path.dirname(texfile),  'test8.pdf')
		self.assertIsNotNone(texfile)
		self.__cleanTmpLatexFile(texfile)
		root_dep_file,  deps = self.maker.compute_dependencies(texfile,  False)
		self.assertEquals(pdffile,  root_dep_file)
		self.assertIsNotNone(deps)
		self.assertDependency(deps, texfile,  'tex',  set([
			os.path.join(os.path.dirname(texfile),  'test5.bbl'),
		]))

	def test_compute_dependencies_12(self):
		texfile = genutils.findFileInPath("test12.tex")
		pdffile = os.path.join(os.path.dirname(texfile),  'test12.pdf')
		self.assertIsNotNone(texfile)
		self.__cleanTmpLatexFile(texfile)
		root_dep_file,  deps = self.maker.compute_dependencies(texfile,  True)
		self.assertEquals(pdffile,  root_dep_file)
		self.assertIsNotNone(deps)
		self.assertDependency(deps, texfile,  'tex',  set([
			os.path.join(os.path.dirname(texfile),  'test5.bbl'), 
			genutils.basename2(texfile,  '.tex') + '.ind', 
			genutils.basename2(texfile,  '.tex') + '.gls', 
			os.path.join(os.path.dirname(texfile),  'test12a.tex'), 
			os.path.join(os.path.dirname(texfile),  'test12b.tex'), 
		]))

	def test_run_translators_0(self):
		# Generate all images from nothing
		try:
			self.config.translators.ignoreSystemTranslators = False
			self.__cleanTmpFigureFile(self.config.translators.imagePaths)
			images = self.maker.run_translators(False)
			#
			src1 = os.path.join(self.config.translators.imagePaths[0],  'english.png.gz')
			src2 = os.path.join(self.config.translators.imagePaths[0],  'subfolder', 'french.png.gz')
			gen1 = os.path.join(self.config.translators.imagePaths[0],  'english.png')
			gen2 = os.path.join(self.config.translators.imagePaths[0],  'subfolder', 'french.png')
			#
			self.assertIsNotNone(images)
			self.assertEqual(2,  len(images))
			self.assertTrue(src1 in images)
			self.assertTrue(src2 in images)
			self.assertEqual(gen1,  images[src1])
			self.assertEqual(gen2,  images[src2])
			#
			self.assertIsFile(gen1)
			self.assertIsFile(gen2)
		finally:
			self.__cleanTmpFigureFile(self.config.translators.imagePaths)

	def test_run_translators_1(self):
		# Generate some images from nothing, the other images are available
		try:
			src1 = os.path.join(self.config.translators.imagePaths[0],  'english.png.gz')
			src2 = os.path.join(self.config.translators.imagePaths[0],  'subfolder', 'french.png.gz')
			gen1 = os.path.join(self.config.translators.imagePaths[0],  'english.png')
			gen2 = os.path.join(self.config.translators.imagePaths[0],  'subfolder', 'french.png')
			# Generate all images
			self.config.translators.ignoreSystemTranslators = False
			self.__cleanTmpFigureFile(self.config.translators.imagePaths)
			self.maker.run_translators(False)
			englishChg0 = genutils.getFileLastChange(gen1)
			frenchChg0 = genutils.getFileLastChange(gen2)
			# Remove one of the generated images
			genutils.unlink(gen1)
			# Wait 1 sec to be sure that the change timestamps are different
			time.sleep(1)
			# Generate the missed images
			images = self.maker.run_translators(False)
			#
			self.assertIsNotNone(images)
			self.assertEqual(2,  len(images))
			self.assertTrue(src1 in images)
			self.assertTrue(src2 in images)
			self.assertEqual(gen1,  images[src1])
			self.assertIsNone(images[src2])
			#
			self.assertIsFile(gen1)
			self.assertIsFile(gen2)
			englishChg1 = genutils.getFileLastChange(gen1)
			frenchChg1 = genutils.getFileLastChange(gen2)
			self.assertGreater(englishChg1,  englishChg0)
			self.assertEqual(frenchChg0,  frenchChg1)
		finally:
			self.__cleanTmpFigureFile(self.config.translators.imagePaths)

	def test_run_translators_2(self):
		# Refresh some image because the source has changed
		try:
			src1 = os.path.join(self.config.translators.imagePaths[0],  'english.png.gz')
			src2 = os.path.join(self.config.translators.imagePaths[0],  'subfolder', 'french.png.gz')
			gen1 = os.path.join(self.config.translators.imagePaths[0],  'english.png')
			gen2 = os.path.join(self.config.translators.imagePaths[0],  'subfolder', 'french.png')
			# Generate all images
			self.config.translators.ignoreSystemTranslators = False
			self.__cleanTmpFigureFile(self.config.translators.imagePaths)
			self.maker.run_translators(False)
			englishChg0 = genutils.getFileLastChange(gen1)
			frenchChg0 = genutils.getFileLastChange(gen2)
			# Wait 1 sec to be sure that the change timestamps are different
			time.sleep(1)
			# Touch one of the source images for forcing it to be regenerated
			Path(src1).touch()
			# Generate the missed images
			images = self.maker.run_translators(False)
			#
			self.assertIsNotNone(images)
			self.assertEqual(2,  len(images))
			self.assertTrue(src1 in images)
			self.assertTrue(src2 in images)
			self.assertEqual(gen1,  images[src1])
			self.assertIsNone(images[src2])
			#
			self.assertIsFile(src1)
			self.assertIsFile(src2)
			englishChg1 = genutils.getFileLastChange(gen1)
			frenchChg1 = genutils.getFileLastChange(gen2)
			self.assertEqual(frenchChg0,  frenchChg1)
			self.assertGreater(englishChg1,  englishChg0)
		finally:
			self.__cleanTmpFigureFile(self.config.translators.imagePaths)

	def test_run_translators_3(self):
		# Force the generation of images
		try:
			src1 = os.path.join(self.config.translators.imagePaths[0],  'english.png.gz')
			src2 = os.path.join(self.config.translators.imagePaths[0],  'subfolder', 'french.png.gz')
			gen1 = os.path.join(self.config.translators.imagePaths[0],  'english.png')
			gen2 = os.path.join(self.config.translators.imagePaths[0],  'subfolder', 'french.png')
			# Generate all images
			self.config.translators.ignoreSystemTranslators = False
			self.__cleanTmpFigureFile(self.config.translators.imagePaths)
			self.maker.run_translators(False)
			englishChg0 = genutils.getFileLastChange(gen1)
			frenchChg0 = genutils.getFileLastChange(gen2)
			# Wait 1 sec to be sure that the change timestamps are different
			time.sleep(1)
			# Generate the missed images
			images = self.maker.run_translators(True)
			#
			self.assertIsNotNone(images)
			self.assertEqual(2,  len(images))
			self.assertTrue(src1 in images)
			self.assertTrue(src2 in images)
			self.assertEqual(gen1, images[src1])
			self.assertEqual(gen2, images[src2])
			#
			self.assertIsFile(gen1)
			self.assertIsFile(gen2)
			englishChg1 = genutils.getFileLastChange(gen1)
			frenchChg1 = genutils.getFileLastChange(gen2)
			self.assertGreater(frenchChg1,  frenchChg0)
			self.assertGreater(englishChg1,  englishChg0)
		finally:
			self.__cleanTmpFigureFile(self.config.translators.imagePaths)

	def test_read_build_stamps(self):
		stamps = self.maker.read_build_stamps(self.dev_ressources_dir,  'stamps.txt')
		self.assertTrue('bib' in stamps)
		self.assertEqual(1,  len(stamps['bib']))
		self.assertTrue('abc' in stamps['bib'])
		self.assertEqual('124',  stamps['bib']['abc'])
		self.assertTrue('idx' in stamps)
		self.assertEqual(2,  len(stamps['idx']))
		self.assertTrue('def' in stamps['idx'])
		self.assertEqual('567',  stamps['idx']['def'])
		self.assertTrue('xyz' in stamps['idx'])
		self.assertEqual('245',  stamps['idx']['xyz'])

	def test_write_build_stamps(self):
		tmpfile = os.path.join(self.dev_ressources_dir,  'tmpstamps.txt')
		try:
			stamps = {
				'bib': {
					'abc': 123, 
				}, 
				'idx': {
					'def': 567, 
					'xyz': 5678, 
				}
			}
			self.maker.write_build_stamps(self.dev_ressources_dir,  'tmpstamps.txt',  stamps)
			with open(tmpfile,  'r') as sf:
				content = sf.read()
			self.assertEqual("BIB(123):abc\nIDX(567):def\nIDX(5678):xyz\n",
				content)
		finally:
			genutils.unlink(tmpfile)

	def test_build_internal_execution_list_12_1(self):
		texfile = genutils.findFileInPath("test12.tex")
		self.assertIsNotNone(texfile)
		self.__cleanTmpLatexFile(texfile)
		#
		root_pdf,  deps = self.maker.compute_dependencies(texfile,  True)
		self.assertIsNotNone(deps)
		# Force building flag
		build_list = self.maker.build_internal_execution_list(texfile,  root_pdf,  deps,  True)
		self.assertIsNotNone(build_list)
		self.assertEqual(4,  len(build_list))
		self.assertEqual(os.path.join(self.dev_ressources_dir,  'test5.bbl'),  build_list[0].output_filename)
		self.assertEqual(os.path.join(self.dev_ressources_dir,  'test12.ind'),  build_list[1].output_filename)
		self.assertEqual(os.path.join(self.dev_ressources_dir,  'test12.gls'),  build_list[2].output_filename)
		self.assertEqual(os.path.join(self.dev_ressources_dir,  'test12.pdf'),  build_list[3].output_filename)

	def test_run_dvips_5(self):
		texfile = genutils.findFileInPath("test5.tex")
		self.assertIsNotNone(texfile)
		self.__cleanTmpLatexFile(texfile)
		self.config.generation.pdfMode = False
		try:
			# Run LaTeX tool prior to the DVIPS tool
			self.maker.run_latex(texfile,  False)
			dvifile = genutils.findFileInPath("test5.dvi")
			self.assertIsNotNone(dvifile)
			# Run DVIPS
			error = self.maker.run_dvips(dvifile)
			self.assertIsNone(error)
			self.assertEqual(0, len(self.maker.standardWarnings))
			self.assertEqual(0, len(self.maker.extendedWarnings))
			psfile = genutils.findFileInPath("test5.ps")
			self.assertIsNotNone(psfile)
		finally:
			self.__cleanTmpLatexFile(texfile)


if __name__ == '__main__':
    unittest.main()

