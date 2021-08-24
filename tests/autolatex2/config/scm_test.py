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

from autolatex2.config import scm

class TestScmConfig(unittest.TestCase):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.__config = None

	def setUp(self):
		logging.getLogger().setLevel(logging.CRITICAL)
		self.__config = scm.ScmConfig()

	@property
	def config(self) -> scm.ScmConfig:
		return self.__config

	def test_get_commitCLI(self):
		self.assertEqual(list(),  self.config.commitCLI)

	def test_set_commitCLI(self):
		self.config.commitCLI = None
		self.assertEqual([],  self.config.commitCLI)
		self.config.commitCLI = list(['a',  'b'])
		self.assertEqual(list(['a',  'b']),  self.config.commitCLI)
		self.config.commitCLI = 'a b'
		self.assertEqual(list(['a',  'b']),  self.config.commitCLI)

	def test_get_updateCLI(self):
		self.assertEqual(list(),  self.config.updateCLI)

	def test_set_updateCLI(self):
		self.config.updateCLI = None
		self.assertEqual([],  self.config.updateCLI)
		self.config.updateCLI = list(['a',  'b'])
		self.assertEqual(list(['a',  'b']),  self.config.updateCLI)
		self.config.updateCLI = 'a b'
		self.assertEqual(list(['a',  'b']),  self.config.updateCLI)


if __name__ == '__main__':
    unittest.main()

