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

from autolatex2.config import clean

class TestCleanConfig(unittest.TestCase):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.__config = None

	def setUp(self):
		logging.getLogger().setLevel(logging.CRITICAL)
		self.__config = clean.CleanConfig()

	@property
	def config(self) -> clean.CleanConfig:
		return self.__config

	def test_get_cleanFiles(self):
		self.assertEqual(list(),  self.config.cleanFiles)

	def test_set_cleanFiles(self):
		self.config.cleanFiles = None
		self.assertEqual([],  self.config.cleanFiles)
		self.config.cleanFiles = list(['a',  'b'])
		self.assertEqual(list(['a',  'b']),  self.config.cleanFiles)
		self.config.cleanFiles = 'a' + os.pathsep + 'b'
		self.assertEqual(list(['a', 'b']),  self.config.cleanFiles)

	def test_get_cleanallFiles(self):
		self.assertEqual(list(),  self.config.cleanallFiles)

	def test_set_cleanallFiles(self):
		self.config.cleanallFiles = None
		self.assertEqual([],  self.config.cleanallFiles)
		self.config.cleanallFiles = list(['a',  'b'])
		self.assertEqual(list(['a',  'b']),  self.config.cleanallFiles)
		self.config.cleanallFiles = 'a' + os.pathsep + 'b'
		self.assertEqual(list(['a', 'b']),  self.config.cleanallFiles)


if __name__ == '__main__':
    unittest.main()

