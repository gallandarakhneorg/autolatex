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

from autolatex2.config import generation

import autolatex2.utils.debug as debug

class TestGenerationConfig(unittest.TestCase):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.__config = None

	def setUp(self):
		logging.getLogger().setLevel(logging.CRITICAL)
		self.__config = generation.GenerationConfig()

	@property
	def config(self) -> generation.GenerationConfig:
		return self.__config

	def test_get_pdfMode(self):
		self.assertTrue(self.config.pdfMode)

	def test_set_pdfMode(self):
		self.config.pdfMode = False
		self.assertFalse(self.config.pdfMode)		
		self.config.pdfMode = True
		self.assertTrue(self.config.pdfMode)		
		self.config.pdfMode = False
		self.assertFalse(self.config.pdfMode)		
		self.config.pdfMode = True
		self.assertTrue(self.config.pdfMode)		



if __name__ == '__main__':
    unittest.main()

