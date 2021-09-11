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



##############################################################
##
class TestTranslatorS2T(unittest.TestCase):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.translator = None
		self.config = None

	def setUp(self):
		logging.getLogger().setLevel(logging.CRITICAL)
		self.config = Config()
		self.config.translators.is_translator_fileformat_1_enable = True
		self.translator = Translator("s2t", self.config)

	def test_name(self):
		self.assertEqual('s2t', self.translator.name)

	def test_source(self):
		self.assertEqual('s', self.translator.source)

	def test_fullSource(self):
		self.assertEqual('s', self.translator.fullSource)

	def test_target(self):
		self.assertEqual('t', self.translator.target)

	def test_variante(self):
		self.assertEqual('', self.translator.variante)

	def test_basename(self):
		self.assertEqual('s2t', self.translator.basename)


##############################################################
##
class TestTranslatorS2TpX(unittest.TestCase):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.config = None

	def setUp(self):
		logging.getLogger().setLevel(logging.CRITICAL)
		self.config = Config()
		self.config.translators.is_translator_fileformat_1_enable = True

	def test_name(self):
		targets = ['u', 'tex', 'layers', 'tex+layers', 'layers+tex']
		for t2 in targets:
			translator = Translator("s2t+"+t2, self.config)
			with self.subTest(target2=t2):
				self.assertEqual('s2t+'+t2, translator.name)

	def test_source(self):
		targets = ['u', 'tex', 'layers', 'tex+layers', 'layers+tex']
		for t2 in targets:
			translator = Translator("s2t+"+t2, self.config)
			with self.subTest(target2=t2):
				self.assertEqual('s', translator.source)

	def test_fullSource(self):
		targets = {'u': 's', 'tex': 'ltx.s', 'layers': 'layers.s',
		           'tex+layers': 'layers.ltx.s', 'layers+tex': 'layers.ltx.s'}
		for t2 in targets:
			translator = Translator("s2t+"+t2, self.config)
			with self.subTest(target2=t2):
				self.assertEqual(targets[t2], translator.fullSource)

	def test_target(self):
		targets = {'u': 't+u', 'tex': 't', 'layers': 't',
		           'tex+layers': 't', 'layers+tex': 't'}
		for t2 in targets:
			translator = Translator("s2t+"+t2, self.config)
			with self.subTest(target2=t2):
				self.assertEqual(targets[t2], translator.target)

	def test_variante(self):
		targets = ['u', 'tex', 'layers', 'tex+layers', 'layers+tex']
		for t2 in targets:
			translator = Translator("s2t+"+t2, self.config)
			with self.subTest(target2=t2):
				self.assertEqual('', translator.variante)

	def test_basename(self):
		targets = ['u', 'tex', 'layers', 'tex+layers', 'layers+tex']
		for t2 in targets:
			translator = Translator("s2t+"+t2, self.config)
			with self.subTest(target2=t2):
				self.assertEqual('s2t'+t2, translator.basename)


##############################################################
##
class TestTranslatorS2TuV(unittest.TestCase):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.config = None
		self.translator = None

	def setUp(self):
		logging.getLogger().setLevel(logging.CRITICAL)
		self.config = Config()
		self.config.translators.is_translator_fileformat_1_enable = True
		self.translator = Translator("s2t_v", self.config)

	def test_name(self):
		self.assertEqual('s2t_v', self.translator.name)

	def test_source(self):
		self.assertEqual('s', self.translator.source)

	def test_fullSource(self):
		self.assertEqual('s', self.translator.fullSource)

	def test_target(self):
		self.assertEqual('t', self.translator.target)

	def test_variante(self):
		self.assertEqual('v', self.translator.variante)

	def test_basename(self):
		self.assertEqual('s2t', self.translator.basename)


##############################################################
##
class TestTranslatorS2TpXuV(unittest.TestCase):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.config = None

	def setUp(self):
		logging.getLogger().setLevel(logging.CRITICAL)
		self.config = Config()
		self.config.translators.is_translator_fileformat_1_enable = True

	def test_name(self):
		targets = ['u', 'tex', 'layers', 'tex+layers', 'layers+tex']
		for t2 in targets:
			translator = Translator("s2t+"+t2+"_v", self.config)
			with self.subTest(target2=t2):
				self.assertEqual('s2t+'+t2+"_v", translator.name)

	def test_source(self):
		targets = ['u', 'tex', 'layers', 'tex+layers', 'layers+tex']
		for t2 in targets:
			translator = Translator("s2t+"+t2+"_v", self.config)
			with self.subTest(target2=t2):
				self.assertEqual('s', translator.source)

	def test_fullSource(self):
		targets = {'u': 's', 'tex': 'ltx.s', 'layers': 'layers.s',
		           'tex+layers': 'layers.ltx.s', 'layers+tex': 'layers.ltx.s'}
		for t2 in targets:
			translator = Translator("s2t+"+t2+"_v", self.config)
			with self.subTest(target2=t2):
				self.assertEqual(targets[t2], translator.fullSource)

	def test_target(self):
		targets = {'u': 't+u', 'tex': 't', 'layers': 't',
		           'tex+layers': 't', 'layers+tex': 't'}
		for t2 in targets:
			translator = Translator("s2t+"+t2+"_v", self.config)
			with self.subTest(target2=t2):
				self.assertEqual(targets[t2], translator.target)

	def test_variante(self):
		targets = ['u', 'tex', 'layers', 'tex+layers', 'layers+tex']
		for t2 in targets:
			translator = Translator("s2t+"+t2+"_v", self.config)
			with self.subTest(target2=t2):
				self.assertEqual('v', translator.variante)

	def test_basename(self):
		targets = ['u', 'tex', 'layers', 'tex+layers', 'layers+tex']
		for t2 in targets:
			translator = Translator("s2t+"+t2+"_v", self.config)
			with self.subTest(target2=t2):
				self.assertEqual('s2t'+t2, translator.basename)


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




if __name__ == '__main__':
    unittest.main()

