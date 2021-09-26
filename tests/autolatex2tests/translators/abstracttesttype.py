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
from abc import abstractmethod

from autolatex2.config.configobj import Config
from autolatex2.translator.translatorrepository import TranslatorRepository
from autolatex2.translator.translatorrunner import TranslatorRunner
import autolatex2.utils.utilfunctions as genutils

class AbstractTranslatorTest(unittest.TestCase):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.__folder_name = None
		self.__trans = None
		self.__root = None
		self.__imgdir = None
		self.__source_image = None
		self.__dest_imege = None
		self.__config = None
		self.__repository = None
		self.__runner = None

	@abstractmethod
	def get_translator_name(self) -> str:
		return None

	def get_translator_test_folder(self) -> str:
		return self.get_translator_name()

	@abstractmethod
	def get_input_filename(self) -> str:
		raise Exception('Implement in subclass')

	@abstractmethod
	def get_output_filename(self) -> str:
		raise Exception('Implement in subclass')

	def __initialize_inclusions(self):
		pass

	def setUp(self):
		logging.getLogger().setLevel(logging.CRITICAL)
		name = self.get_translator_name()
		if name:
			self.__folder_name = self.get_translator_test_folder()
			self.__trans = name
			self.__config = Config()
			self.__root = os.path.join(os.path.dirname(__file__),  'dev-resources')
			self.__config.documentDirectory = self.__root
			self.__imgdir = os.path.join(self.__root,  self.__folder_name)
			self.__source_image = os.path.join(self.__imgdir,  self.get_input_filename())
			self.__dest_image = os.path.join(self.__imgdir,  self.get_output_filename())
			self.__config.translators.addImagePath(self.__imgdir)
			self.__initialize_inclusions()
			self.__repository = TranslatorRepository(self.__config)
			self.__runner = TranslatorRunner(self.__repository)
			self.__runner.sync(detect_conflicts = False)
		else:
			self.__folder_name = None
			self.__trans = None

	def tearDown(self):
		self.__folder_name = None
		self.__trans = None
		self.__root = None
		self.__imgdir = None
		self.__source_image = None
		self.__dest_imege = None
		self.__config = None
		self.__repository = None
		self.__runner = None

	def test_generation(self):
		if self.__runner:
			images = self.__runner.getSourceImages()
			self.assertEqual(set([self.__source_image]),  images)
			for image in images:
				self.assertFalse(os.path.isfile(self.__dest_image))
				r = self.__runner.generateImage(translatorName = self.__trans,  infile = image, outfile = self.__dest_image, onlymorerecent = False, failOnError = True)
				self.assertIsNotNone(r)
				self.assertEquals(self.__dest_image,  str(r))
				try:
					self.assertTrue(os.path.isfile(self.__dest_image))
				finally:
					for tmpfile in self.__runner.getTemporaryFiles(translatorName = self.__trans,  infile = image, outfile = self.__dest_image):
						genutils.unlink(tmpfile)
					for tmpfile in self.__runner.getTargetFiles(translatorName = self.__trans,  infile = image, outfile = self.__dest_image):
						genutils.unlink(tmpfile)

