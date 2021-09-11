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
import time

import autolatex2.utils.utilfunctions as genutils
from autolatex2.utils.extlogging import ensureAutoLaTeXLoggingLevels
from autolatex2.translator.translatorobj import *
from autolatex2.translator.translatorrepository import *
from autolatex2.translator.translatorrunner import *
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
		f.write(textwrap.dedent('''\
			INPUT_EXTENSIONS = .svg
			OUTPUT_EXTENSIONS = .pdf
			TRANSLATOR_FUNCTION with perl =<<EOL
			{ local *FILE;
			  open(*FILE, "> $out") or die("$out: $!\n");
			  print FILE "CONTENT\\n";
			  close(*FILE);
			}
			EOL
			'''))
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
		self.config = Config()
		self.config.translators.is_translator_fileformat_1_enable = True
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


	def __assert_gtf(self,  filename : str,  translator_name : str):
		expected = self.repo._getObjectFor(translator_name)
		actual = self.runner.getTranslatorFor(filename)
		self.assertEqual(expected, actual)
		
	def test_getTranslatorFor(self):
		self.__assert_gtf('img1.svg', 'svg2pdf')
		self.__assert_gtf('img1.svg+tex',  'svg2pdf+tex')
		self.__assert_gtf('img1+tex.svg', 'svg2pdf+tex')
		self.__assert_gtf('img1.tex.svg', 'svg2pdf+tex')
		self.__assert_gtf('img1_tex.svg', 'svg2pdf')
		self.__assert_gtf('img1.svgz', 'svg2pdf')


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
		ensureAutoLaTeXLoggingLevels()
		logging.getLogger().setLevel(logging.CRITICAL)
		self.directory1 = generateTranslatorStubsForGeneration()
		self.directory2 = generateImageStubs()
		self.config = Config()
		self.config.translators.is_translator_fileformat_1_enable = True
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
		self.config.translators.setIncluded('svg2pdf_cli', TranslatorLevel.SYSTEM, True)
		self.config.translators.setIncluded('svg2pdf_python', TranslatorLevel.SYSTEM, False)
		self.config.translators.setIncluded('svg2pdf_perl', TranslatorLevel.SYSTEM, False)
		self.runner.sync()
		self.assertEqual(
				os.path.join(self.directory2, 'img1.pdf'),
				self.runner.generateImage(infile=os.path.join(self.directory2, 'img1.svg'), onlymorerecent=False))
		self.assertTrue(os.path.isfile(os.path.join(self.directory2, 'img1.pdf')))

	def test_generateImages_python_force(self):
		self.config.translators.setIncluded('svg2pdf_cli', TranslatorLevel.SYSTEM, False)
		self.config.translators.setIncluded('svg2pdf_python', TranslatorLevel.SYSTEM, True)
		self.config.translators.setIncluded('svg2pdf_perl', TranslatorLevel.SYSTEM, False)
		self.runner.sync()
		self.assertEqual(
				os.path.join(self.directory2, 'img1.pdf'),
				self.runner.generateImage(infile=os.path.join(self.directory2, 'img1.svg'), onlymorerecent=False))
		self.assertTrue(os.path.isfile(os.path.join(self.directory2, 'img1.pdf')))

	def test_generateImages_perl_force(self):
		self.config.translators.setIncluded('svg2pdf_cli', TranslatorLevel.SYSTEM, False)
		self.config.translators.setIncluded('svg2pdf_python', TranslatorLevel.SYSTEM, False)
		self.config.translators.setIncluded('svg2pdf_perl', TranslatorLevel.SYSTEM, True)
		self.runner.sync()
		self.assertEqual(
				os.path.join(self.directory2, 'img1.pdf'),
				self.runner.generateImage(infile=os.path.join(self.directory2, 'img1.svg'), onlymorerecent=False))
		self.assertTrue(os.path.isfile(os.path.join(self.directory2, 'img1.pdf')))

	def test_generateImages_cli_noForce(self):
		self.config.translators.setIncluded('svg2pdf_cli', TranslatorLevel.SYSTEM, True)
		self.config.translators.setIncluded('svg2pdf_python', TranslatorLevel.SYSTEM, False)
		self.config.translators.setIncluded('svg2pdf_perl', TranslatorLevel.SYSTEM, False)
		self.runner.sync()
		self.runner.generateImage(infile=os.path.join(self.directory2, 'img1.svg'), onlymorerecent=False)
		lastChange = genutils.getFileLastChange(os.path.join(self.directory2, 'img1.pdf'))
		time.sleep(1)
		self.assertIsNone(
				self.runner.generateImage(infile=os.path.join(self.directory2, 'img1.svg')))
		self.assertTrue(os.path.isfile(os.path.join(self.directory2, 'img1.pdf')))
		lastChange2 = genutils.getFileLastChange(os.path.join(self.directory2, 'img1.pdf'))
		self.assertEqual(lastChange, lastChange2)

	def test_generateImages_python_noForce(self):
		self.config.translators.setIncluded('svg2pdf_cli', TranslatorLevel.SYSTEM, False)
		self.config.translators.setIncluded('svg2pdf_python', TranslatorLevel.SYSTEM, True)
		self.config.translators.setIncluded('svg2pdf_perl', TranslatorLevel.SYSTEM, False)
		self.runner.sync()
		self.runner.generateImage(infile=os.path.join(self.directory2, 'img1.svg'), onlymorerecent=False)
		lastChange = genutils.getFileLastChange(os.path.join(self.directory2, 'img1.pdf'))
		time.sleep(1)
		self.assertIsNone(
				self.runner.generateImage(infile=os.path.join(self.directory2, 'img1.svg')))
		self.assertTrue(os.path.isfile(os.path.join(self.directory2, 'img1.pdf')))
		lastChange2 = genutils.getFileLastChange(os.path.join(self.directory2, 'img1.pdf'))
		self.assertEqual(lastChange, lastChange2)

	def test_generateImages_perl_noForce(self):
		self.config.translators.setIncluded('svg2pdf_cli', TranslatorLevel.SYSTEM, False)
		self.config.translators.setIncluded('svg2pdf_python', TranslatorLevel.SYSTEM, False)
		self.config.translators.setIncluded('svg2pdf_perl', TranslatorLevel.SYSTEM, True)
		self.runner.sync()
		self.runner.generateImage(infile=os.path.join(self.directory2, 'img1.svg'), onlymorerecent=False)
		lastChange = genutils.getFileLastChange(os.path.join(self.directory2, 'img1.pdf'))
		time.sleep(1)
		self.assertIsNone(
				self.runner.generateImage(infile=os.path.join(self.directory2, 'img1.svg')))
		self.assertTrue(os.path.isfile(os.path.join(self.directory2, 'img1.pdf')))
		lastChange2 = genutils.getFileLastChange(os.path.join(self.directory2, 'img1.pdf'))
		self.assertEqual(lastChange, lastChange2)


if __name__ == '__main__':
    unittest.main()

