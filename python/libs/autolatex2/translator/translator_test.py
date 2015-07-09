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
import tempfile
import shutil
import textwrap
import time

from autolatex2.translator.translator import *
from autolatex2.config.config import *

from autolatex2.utils import debug

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


def generateTranslatorStubsForGeneration():
	directory = tempfile.mkdtemp()
	with open(os.path.join(directory, "svg2pdf_cli.transdef"), 'w') as f:
		f.write(textwrap.dedent("""\
			INPUT_EXTENSIONS = .svg
			OUTPUT_EXTENSIONS = .pdf
			COMMAND_LINE = touch $out
			"""))
		f.flush()
	with open(os.path.join(directory, "svg2pdf_python.transdef"), 'w') as f:
		f.write(textwrap.dedent("""\
			INPUT_EXTENSIONS = .svg
			OUTPUT_EXTENSIONS = .pdf
			TRANSLATOR_FUNCTION with python =<<EOL
			with open(_out, 'w') as f:
				f.write("CONTENT\\n")
			EOL
			"""))
		f.flush()
	with open(os.path.join(directory, "svg2pdf_perl.transdef"), 'w') as f:
		f.write(textwrap.dedent("""\
			INPUT_EXTENSIONS = .svg
			OUTPUT_EXTENSIONS = .pdf
			TRANSLATOR_FUNCTION with perl =<<EOL
			{ local *FILE;
			  open(*FILE, "> $out") or die("$out: $!\n");
			  print FILE "CONTENT\\n";
			  close(*FILE);
			}
			EOL
			"""))
		f.flush()
	return directory

def generateImageStubs():
	directory = tempfile.mkdtemp()
	with open(os.path.join(directory, "img1.svg"), 'w') as f:
		f.write("")
		f.flush()
	with open(os.path.join(directory, "img2.svg+tex"), 'w') as f:
		f.write("")
		f.flush()
	subdir = os.path.join(directory, 'subdir')
	os.makedirs(subdir)
	with open(os.path.join(subdir, "img3.dot"), 'w') as f:
		f.write("")
		f.flush()
	with open(os.path.join(subdir, "img4+tex.svg"), 'w') as f:
		f.write("")
		f.flush()
	with open(os.path.join(subdir, "img5.unsupported"), 'w') as f:
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
		self.config = config.Config()
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
		self.config = config.Config()

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
		self.config = config.Config()
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
		self.config = config.Config()

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
		self.config = config.Config()
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
		self.config = config.Config()
		self.repo = TranslatorRepository(self.config)
		translators = self.repo._readDirectory(directory=self.directory, recursive=True, warn=False)
		for translator in translators:
			self.repo._installedTranslators[1][translator] = translators[translator]
			self.repo._installedTranslatorNames.add(translator)

	def tearDown(self):
		if self.directory is not None:
			shutil.rmtree(self.directory)
			self.directory = None

	def test__getIncludedTranslators_noConfig(self):
		included = self.repo._getIncludedTranslators()
		self.assertDictEqual({
				'svg2pdf': TranslatorLevel.user,
				'svg2pdf+tex': TranslatorLevel.user,
				'dot2pdf': TranslatorLevel.user,
				'uml2pdf_umbrello': TranslatorLevel.user,
				}, included)

	def test__getIncludedTranslators_config(self):
		self.config.translators.setIncluded('svg2pdf', TranslatorLevel.system.value, False)
		self.config.translators.setIncluded('svg2pdf', TranslatorLevel.document.value, True)
		self.config.translators.setIncluded('dot2pdf', TranslatorLevel.user.value, False)
		included = self.repo._getIncludedTranslators()
		self.assertDictEqual({
				'svg2pdf': TranslatorLevel.document,
				'svg2pdf+tex': TranslatorLevel.user,
				'uml2pdf_umbrello': TranslatorLevel.user,
				}, included)

	def test__buildIncludedTranslatorDict(self):
		svg2pdf = self.repo._getObjectFor('svg2pdf')
		texsvg2pdf = self.repo._getObjectFor('svg2pdf+tex')
		uml2pdf = self.repo._getObjectFor('uml2pdf_umbrello')
		self.config.translators.setIncluded('svg2pdf', TranslatorLevel.system.value, False)
		self.config.translators.setIncluded('svg2pdf', TranslatorLevel.document.value, True)
		self.config.translators.setIncluded('dot2pdf', TranslatorLevel.user.value, False)
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
		self.config = config.Config()
		self.repo = TranslatorRepository(self.config)
		translators = self.repo._readDirectory(directory=self.directory, recursive=True, warn=False)
		for translator in translators:
			self.repo._installedTranslators[1][translator] = translators[translator]
			self.repo._installedTranslatorNames.add(translator)
		self.config.translators.setIncluded('svg2pdf', TranslatorLevel.system.value, False)
		self.config.translators.setIncluded('svg2pdf', TranslatorLevel.document.value, True)
		self.config.translators.setIncluded('svg2png', TranslatorLevel.system.value, True)
		self.config.translators.setIncluded('dot2pdf', TranslatorLevel.user.value, False)

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
		svg2pdf = self.repo._getObjectFor('svg2pdf')
		svg2png = self.repo._getObjectFor('svg2png')
		conflicts = self.repo._detectConflicts()
		with self.assertRaises(TranslatorConflictError):
			self.repo._failOnConflict(conflicts[TranslatorLevel.document.value], 'myfilename.cfg')


##############################################################
##
class TestTranslatorRunner(unittest.TestCase):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.directory1 = None
		self.directory2 = None
		self.repo = None
		self.runner = None
		self.config = None

	def setUp(self):
		logging.getLogger().setLevel(logging.CRITICAL)
		self.directory1 = generateTranslatorStubs()
		self.directory2 = generateImageStubs()
		self.config = config.Config()
		self.config.translators.ignoreSystemTranslators = True
		self.config.translators.ignoreUserTranslators = True
		self.config.translators.ignoreDocumentTranslators = True
		self.config.translators.includePaths = [ self.directory1 ]
		self.config.translators.imagePaths = [ self.directory2 ]
		self.repo = TranslatorRepository(self.config)
		self.runner = TranslatorRunner(self.repo)
		self.runner.sync()

	def tearDown(self):
		if self.directory1 is not None:
			shutil.rmtree(self.directory1)
			self.directory1 = None
		if self.directory2 is not None:
			shutil.rmtree(self.directory2)
			self.directory2 = None


	def test_getSourceImages_notRecursive(self):
		self.config.translators.recursiveImagePath = False
		images = self.runner.getSourceImages()
		self.assertSetEqual(
			{	os.path.join(self.directory2, 'img1.svg'),
				os.path.join(self.directory2, 'img2.svg+tex'),
			}, images)


	def test_getSourceImages_recursive(self):
		self.config.translators.recursiveImagePath = True
		images = self.runner.getSourceImages()
		self.assertSetEqual(
			{	os.path.join(self.directory2, 'img1.svg'),
				os.path.join(self.directory2, 'img2.svg+tex'),
				os.path.join(self.directory2, 'subdir', 'img3.dot'),
				os.path.join(self.directory2, 'subdir', 'img4+tex.svg'),
			}, images)


	def test_getTranslatorFor(self):
		translator = self.runner.getTranslatorFor('img1.svg')
		self.assertEqual(self.repo._getObjectFor('svg2pdf'), translator)
		translator = self.runner.getTranslatorFor('img1.svg+tex')
		self.assertEqual(self.repo._getObjectFor('svg2pdf+tex'), translator)
		translator = self.runner.getTranslatorFor('img1+tex.svg')
		self.assertEqual(self.repo._getObjectFor('svg2pdf+tex'), translator)
		translator = self.runner.getTranslatorFor('img1.tex.svg')
		self.assertEqual(self.repo._getObjectFor('svg2pdf+tex'), translator)
		translator = self.runner.getTranslatorFor('img1_tex.svg')
		self.assertEqual(self.repo._getObjectFor('svg2pdf'), translator)
		translator = self.runner.getTranslatorFor('img1.svgz')
		self.assertEqual(self.repo._getObjectFor('svg2pdf'), translator)


##############################################################
##
class TestTranslatorRunnerGeneration(unittest.TestCase):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.directory1 = None
		self.directory2 = None
		self.repo = None
		self.runner = None
		self.config = None

	def setUp(self):
		logging.getLogger().setLevel(logging.CRITICAL)
		self.directory1 = generateTranslatorStubsForGeneration()
		self.directory2 = generateImageStubs()
		self.config = config.Config()
		self.config.translators.ignoreSystemTranslators = True
		self.config.translators.ignoreUserTranslators = True
		self.config.translators.ignoreDocumentTranslators = True
		self.config.translators.includePaths = [ self.directory1 ]
		self.config.translators.imagePaths = [ self.directory2 ]
		self.repo = TranslatorRepository(self.config)
		self.runner = TranslatorRunner(self.repo)

	def tearDown(self):
		if self.directory1 is not None:
			shutil.rmtree(self.directory1)
			self.directory1 = None
		if self.directory2 is not None:
			shutil.rmtree(self.directory2)
			self.directory2 = None

	def test_generateImages_cli_force(self):
		self.config.translators.setIncluded('svg2pdf_cli', TranslatorLevel.system.value, True)
		self.config.translators.setIncluded('svg2pdf_python', TranslatorLevel.system.value, False)
		self.config.translators.setIncluded('svg2pdf_perl', TranslatorLevel.system.value, False)
		self.runner.sync()
		self.assertEqual(
				os.path.join(self.directory2, 'img1.pdf'),
				self.runner.generateImage(infile=os.path.join(self.directory2, 'img1.svg'), onlymorerecent=False))
		self.assertTrue(os.path.isfile(os.path.join(self.directory2, 'img1.pdf')))

	def test_generateImages_python_force(self):
		self.config.translators.setIncluded('svg2pdf_cli', TranslatorLevel.system.value, False)
		self.config.translators.setIncluded('svg2pdf_python', TranslatorLevel.system.value, True)
		self.config.translators.setIncluded('svg2pdf_perl', TranslatorLevel.system.value, False)
		self.runner.sync()
		self.assertEqual(
				os.path.join(self.directory2, 'img1.pdf'),
				self.runner.generateImage(infile=os.path.join(self.directory2, 'img1.svg'), onlymorerecent=False))
		self.assertTrue(os.path.isfile(os.path.join(self.directory2, 'img1.pdf')))

	def test_generateImages_perl_force(self):
		self.config.translators.setIncluded('svg2pdf_cli', TranslatorLevel.system.value, False)
		self.config.translators.setIncluded('svg2pdf_python', TranslatorLevel.system.value, False)
		self.config.translators.setIncluded('svg2pdf_perl', TranslatorLevel.system.value, True)
		self.runner.sync()
		self.assertEqual(
				os.path.join(self.directory2, 'img1.pdf'),
				self.runner.generateImage(infile=os.path.join(self.directory2, 'img1.svg'), onlymorerecent=False))
		self.assertTrue(os.path.isfile(os.path.join(self.directory2, 'img1.pdf')))

	def test_generateImages_cli_noForce(self):
		self.config.translators.setIncluded('svg2pdf_cli', TranslatorLevel.system.value, True)
		self.config.translators.setIncluded('svg2pdf_python', TranslatorLevel.system.value, False)
		self.config.translators.setIncluded('svg2pdf_perl', TranslatorLevel.system.value, False)
		self.runner.sync()
		self.runner.generateImage(infile=os.path.join(self.directory2, 'img1.svg'), onlymorerecent=False)
		lastChange = utils.fileLastChange(os.path.join(self.directory2, 'img1.pdf'))
		time.sleep(1)
		self.assertEqual(
				os.path.join(self.directory2, 'img1.pdf'),
				self.runner.generateImage(infile=os.path.join(self.directory2, 'img1.svg')))
		self.assertTrue(os.path.isfile(os.path.join(self.directory2, 'img1.pdf')))
		lastChange2 = utils.fileLastChange(os.path.join(self.directory2, 'img1.pdf'))
		self.assertEqual(lastChange, lastChange2)

	def test_generateImages_python_noForce(self):
		self.config.translators.setIncluded('svg2pdf_cli', TranslatorLevel.system.value, False)
		self.config.translators.setIncluded('svg2pdf_python', TranslatorLevel.system.value, True)
		self.config.translators.setIncluded('svg2pdf_perl', TranslatorLevel.system.value, False)
		self.runner.sync()
		self.runner.generateImage(infile=os.path.join(self.directory2, 'img1.svg'), onlymorerecent=False)
		lastChange = utils.fileLastChange(os.path.join(self.directory2, 'img1.pdf'))
		time.sleep(1)
		self.assertEqual(
				os.path.join(self.directory2, 'img1.pdf'),
				self.runner.generateImage(infile=os.path.join(self.directory2, 'img1.svg')))
		self.assertTrue(os.path.isfile(os.path.join(self.directory2, 'img1.pdf')))
		lastChange2 = utils.fileLastChange(os.path.join(self.directory2, 'img1.pdf'))
		self.assertEqual(lastChange, lastChange2)

	def test_generateImages_perl_noForce(self):
		self.config.translators.setIncluded('svg2pdf_cli', TranslatorLevel.system.value, False)
		self.config.translators.setIncluded('svg2pdf_python', TranslatorLevel.system.value, False)
		self.config.translators.setIncluded('svg2pdf_perl', TranslatorLevel.system.value, True)
		self.runner.sync()
		self.runner.generateImage(infile=os.path.join(self.directory2, 'img1.svg'), onlymorerecent=False)
		lastChange = utils.fileLastChange(os.path.join(self.directory2, 'img1.pdf'))
		time.sleep(1)
		self.assertEqual(
				os.path.join(self.directory2, 'img1.pdf'),
				self.runner.generateImage(infile=os.path.join(self.directory2, 'img1.svg')))
		self.assertTrue(os.path.isfile(os.path.join(self.directory2, 'img1.pdf')))
		lastChange2 = utils.fileLastChange(os.path.join(self.directory2, 'img1.pdf'))
		self.assertEqual(lastChange, lastChange2)


if __name__ == '__main__':
    unittest.main()

