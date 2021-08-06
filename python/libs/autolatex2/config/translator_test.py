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

from autolatex2.config import translator

import autolatex2.utils.debug as debug

class TestTranslatorConfig(unittest.TestCase):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.__config = None

	def setUp(self):
		logging.getLogger().setLevel(logging.CRITICAL)
		self.__config = translator.TranslatorConfig()

	@property
	def config(self) -> translator.TranslatorConfig:
		return self.__config

	def assertFalseNotNone(self, v):
		self.assertIsNotNone(v)
		self.assertFalse(v)




	def test_includePaths_getter(self):
		self.assertListEqual([], self.config.includePaths)

	def test_includePaths_setter(self):
		self.config.includePaths = [ 'a', 'b', 'c' ]
		self.assertListEqual([ 'a', 'b', 'c' ], self.config.includePaths)



	def test_imagePaths_getter(self):
		self.assertListEqual([], self.config.imagePaths)

	def test_imagePaths_setter(self):
		self.config.imagePaths = [ 'a', 'b', 'c' ]
		self.assertListEqual([ 'a', 'b', 'c' ], self.config.imagePaths)



	def test_imagesToConvert_getter(self):
		self.assertSetEqual(set(), self.config.imagesToConvert)

	def test_imagesToConvert_setter(self):
		self.config.imagesToConvert = { 'a', 'b', 'c' }
		self.assertSetEqual({ 'a', 'b', 'c' }, self.config.imagesToConvert)



	def test_setIncluded(self):
		self.config.setIncluded('a', 0, False)
		self.config.setIncluded('a', 1, None)
		self.config.setIncluded('a', 2, True)
		self.config.setIncluded('b', 2, False)

		self.assertListEqual(
			[	{ 'a': False},
				{},
				{ 'a': True, 'b': False},
			], self.config.inclusions)


	def test_included_inheriting(self):
		self.config.setIncluded('a', 0, False)
		self.config.setIncluded('a', 1, None)
		self.config.setIncluded('a', 2, True)
		self.config.setIncluded('b', 2, False)

		self.assertFalseNotNone(self.config.included('a', 0))
		self.assertFalseNotNone(self.config.included('a', 1))
		self.assertTrue(self.config.included('a', 2))
		self.assertIsNone(self.config.included('b', 0))
		self.assertIsNone(self.config.included('b', 1))
		self.assertFalseNotNone(self.config.included('b', 2))
		self.assertIsNone(self.config.included('c', 0))
		self.assertIsNone(self.config.included('c', 1))
		self.assertIsNone(self.config.included('c', 2))

	def test_included_notInheriting(self):
		self.config.setIncluded('a', 0, False)
		self.config.setIncluded('a', 1, None)
		self.config.setIncluded('a', 2, True)
		self.config.setIncluded('b', 2, False)

		self.assertFalseNotNone(self.config.included('a', 0, inherit=False))
		self.assertIsNone(self.config.included('a', 1, inherit=False))
		self.assertTrue(self.config.included('a', 2, inherit=False))
		self.assertIsNone(self.config.included('b', 0, inherit=False))
		self.assertIsNone(self.config.included('b', 1, inherit=False))
		self.assertFalseNotNone(self.config.included('b', 2, inherit=False))
		self.assertIsNone(self.config.included('c', 0, inherit=False))
		self.assertIsNone(self.config.included('c', 1, inherit=False))
		self.assertIsNone(self.config.included('c', 2, inherit=False))


	def test_inclusionLevel_1(self):
		self.config.setIncluded('a', 0, False)
		self.config.setIncluded('a', 1, None)
		self.config.setIncluded('a', 2, True)
		self.config.setIncluded('b', 2, False)

		self.assertEqual(2, self.config.inclusionLevel('a'))
		self.assertEqual(-1, self.config.inclusionLevel('b'))
		self.assertEqual(-2, self.config.inclusionLevel('c'))

	def test_inclusionLevel_2(self):
		self.config.setIncluded('a', 0, False)
		self.config.setIncluded('a', 1, None)
		self.config.setIncluded('a', 2, True)
		self.config.setIncluded('b', 0, False)
		self.config.setIncluded('b', 1, True)

		self.assertEqual(2, self.config.inclusionLevel('a'))
		self.assertEqual(1, self.config.inclusionLevel('b'))
		self.assertEqual(-2, self.config.inclusionLevel('c'))



if __name__ == '__main__':
    unittest.main()

