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
import tempfile
import shutil
import textwrap

from autolatex2.translator.translatorobj import *
from autolatex2.translator.translatorrepository import *
from autolatex2.config.configobj import Config

##############################################################
##
def generateTranslatorStubs():
	directory = tempfile.mkdtemp()
	with open(os.path.join(directory, "svg2pdf.transdef"), 'w') as f:
		f.write("MUST BE OVERRIDDEN")
		f.flush()
	with open(os.path.join(directory, "dot2pdf.transdef"), 'w') as f:
		f.write(textwrap.dedent("""\
			INPUT_EXTENSIONS = .dot

			OUTPUT_EXTENSIONS for pdf = .pdf
			OUTPUT_EXTENSIONs for eps = .eps

			TRANSLATOR_FUNCTION =<<EOL {
				if ($ispdfmode) {
					runCommandOrFail('dot', '-Tpdf', "$in", '-o', "$out");
					1;
				}
				else {
					my $svgFile = File::Spec->catfile(
								dirname($out),
								basename($out,@outexts).'.svg');
					runCommandOrFail('dot', '-Tsvg', "$in", '-o', "$svgFile");
					$transresult = runTranslator('svg2pdf', "$svgFile", "$out");
					unlink("$svgFile");
					$transresult;
				}
			}
			EOL
			"""))
		f.flush()
	subdir = os.path.join(directory, 'subdir')
	os.makedirs(subdir)
	with open(os.path.join(subdir, "svg2pdf.transdef"), 'w') as f:
		f.write(textwrap.dedent("""\
			# Test content only
			INPUT_EXTENSIONS = .svg .svgz

			OUTPUT_EXTENSIONS for pdf = .pdf
			OUTPUT_EXTENSIONS for eps = .eps

			COMMAND_LINE for pdf = inkscape --without-gui --export-area-page --export-pdf "$out" "$in"
			COMMAND_LINE for eps = inkscape --without-gui --export-area-page --export-eps "$out" "$in"
			"""))
		f.flush()
	with open(os.path.join(subdir, "svg2pdf+tex.transdef"), 'w') as f:
		f.write(textwrap.dedent("""\
			INPUT_EXTENSIONS = .svgt .svg_t .svgtex .svg+tex .tex.svg +tex.svg .svgzt .svgz_t .svgztex .svgz+tex .tex.svgz +tex.svgz

			OUTPUT_EXTENSIONS for pdf = .pdf .pdftex_t
			OUTPUT_EXTENSIONS for eps = .eps .pstex_t

			COMMAND_LINE = dosomething

			FILES_TO_CLEAN = $out.pdftex_t $out.pstex_t
			"""))
		f.flush()
	with open(os.path.join(subdir, "uml2pdf_umbrello.transdef"), 'w') as f:
		f.write("")
		f.flush()
	return directory


def generateTranslatorStubsWithConflicts():
	directory = generateTranslatorStubs()
	with open(os.path.join(directory, "svg2png.transdef"), 'w') as f:
		f.write("MUST BE OVERRIDDEN")
		f.flush()
	return directory


##############################################################
##
class TestTranslatorRepositoryInit(unittest.TestCase):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.directory = None
		self.repo = None
		self.config = None

	def setUp(self):
		logging.getLogger().setLevel(logging.CRITICAL)
		self.directory = generateTranslatorStubs()
		self.config = Config()
		self.config.translators.is_translator_fileformat_1_enable = True
		self.repo = TranslatorRepository(self.config)

	def tearDown(self):
		if self.directory is not None:
			shutil.rmtree(self.directory)
			self.directory = None

	def test__readDirectory_noRecursive(self):
		translators = self.repo._readDirectory(directory=self.directory, recursive=False, warn=False)
		self.assertSetEqual(
				{ 'svg2pdf', 'dot2pdf' },
				{ k for (k, v) in translators.items() })
		self.assertEqual(
					os.path.join(self.directory, 'svg2pdf.transdef'),
					translators['svg2pdf'].filename)

	def test__readDirectory_recursive(self):
		translators = self.repo._readDirectory(directory=self.directory, recursive=True, warn=False)
		self.assertSetEqual(
				{ 'svg2pdf', 'dot2pdf', 'svg2pdf+tex', 'uml2pdf_umbrello' },
				{ k for (k, v) in translators.items() })
		self.assertEqual(
					os.path.join(self.directory, 'subdir', 'svg2pdf.transdef'),
					translators['svg2pdf'].filename)



##############################################################
##
class TestTranslatorRepositoryShared(unittest.TestCase):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.directory = None
		self.repo = None
		self.config = None

	def setUp(self):
		logging.getLogger().setLevel(logging.CRITICAL)
		self.directory = generateTranslatorStubs()
		self.config = Config()
		self.config.translators.is_translator_fileformat_1_enable = True
		self.repo = TranslatorRepository(self.config)
		translators = self.repo._readDirectory(directory=self.directory, recursive=True, warn=False)
		for translator in translators:
			self.repo._installedTranslators[TranslatorLevel.USER][translator] = translators[translator]
			self.repo._installedTranslatorNames.add(translator)

	def tearDown(self):
		if self.directory is not None:
			shutil.rmtree(self.directory)
			self.directory = None

	def test_getIncludedTranslatorsWithLevels_noConfig(self):
		included = self.repo.getIncludedTranslatorsWithLevels()
		self.assertDictEqual({
				'svg2pdf': TranslatorLevel.USER,
				'svg2pdf+tex': TranslatorLevel.USER,
				'dot2pdf': TranslatorLevel.USER,
				'uml2pdf_umbrello': TranslatorLevel.USER,
				}, included)

	def test_getIncludedTranslatorsWithLevels_config(self):
		self.config.translators.setIncluded('svg2pdf', TranslatorLevel.SYSTEM, False)
		self.config.translators.setIncluded('svg2pdf', TranslatorLevel.DOCUMENT, True)
		self.config.translators.setIncluded('dot2pdf', TranslatorLevel.USER, False)
		included = self.repo.getIncludedTranslatorsWithLevels()
		self.assertDictEqual({
				'svg2pdf': TranslatorLevel.DOCUMENT,
				'svg2pdf+tex': TranslatorLevel.USER,
				'uml2pdf_umbrello': TranslatorLevel.USER,
				}, included)

	def test__buildIncludedTranslatorDict(self):
		svg2pdf = self.repo._getObjectFor('svg2pdf')
		texsvg2pdf = self.repo._getObjectFor('svg2pdf+tex')
		uml2pdf = self.repo._getObjectFor('uml2pdf_umbrello')
		self.config.translators.setIncluded('svg2pdf', TranslatorLevel.SYSTEM, False)
		self.config.translators.setIncluded('svg2pdf', TranslatorLevel.DOCUMENT, True)
		self.config.translators.setIncluded('dot2pdf', TranslatorLevel.USER, False)
		included = self.repo._buildIncludedTranslatorDict()
		self.assertDictEqual({
				'svg': svg2pdf,
				'ltx.svg': texsvg2pdf,
				'uml': uml2pdf,
				}, included)



##############################################################
##
class TestTranslatorRepositoryConflict(unittest.TestCase):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.directory = None
		self.repo = None
		self.config = None

	def setUp(self):
		logging.getLogger().setLevel(logging.CRITICAL)
		self.directory = generateTranslatorStubsWithConflicts()
		self.config = Config()
		self.config.translators.is_translator_fileformat_1_enable = True
		self.repo = TranslatorRepository(self.config)
		translators = self.repo._readDirectory(directory=self.directory, recursive=True, warn=False)
		for translator in translators:
			self.repo._installedTranslators[1][translator] = translators[translator]
			self.repo._installedTranslatorNames.add(translator)
		self.config.translators.setIncluded('svg2pdf', TranslatorLevel.SYSTEM, False)
		self.config.translators.setIncluded('svg2pdf', TranslatorLevel.DOCUMENT, True)
		self.config.translators.setIncluded('svg2png', TranslatorLevel.SYSTEM, True)
		self.config.translators.setIncluded('dot2pdf', TranslatorLevel.USER, False)

	def tearDown(self):
		if self.directory is not None:
			shutil.rmtree(self.directory)
			self.directory = None

	def test__detectConflicts(self):
		svg2pdf = self.repo._getObjectFor('svg2pdf')
		svg2png = self.repo._getObjectFor('svg2png')
		conflicts = self.repo._detectConflicts()
		self.assertListEqual([
				{},
				{},
				{
					'svg': { svg2pdf, svg2png },
				}], conflicts)

	def test__failOnConflict(self):
		self.repo._getObjectFor('svg2pdf')
		self.repo._getObjectFor('svg2png')
		conflicts = self.repo._detectConflicts()
		with self.assertRaises(TranslatorConflictError):
			self.repo._failOnConflict(conflicts[TranslatorLevel.DOCUMENT], 'myfilename.cfg')


if __name__ == '__main__':
    unittest.main()

