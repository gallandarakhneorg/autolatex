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

from autolatex2.config import logging as loggingcfg

class TestLoggingConfig(unittest.TestCase):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.__config = None

	def setUp(self):
		logging.getLogger().setLevel(logging.CRITICAL)
		self.__config = loggingcfg.LoggingConfig()

	@property
	def config(self) -> loggingcfg.LoggingConfig:
		return self.__config

	def test_get_message(self):
		self.assertEqual('%(levelname)s: %(message)s',  self.config.message)

	def test_set_message(self):
		self.config.message = 'abc'
		self.assertEqual('abc',  self.config.message)
		self.config.message = None
		self.assertEqual('%(levelname)s: %(message)s',  self.config.message)

	def test_get_level(self):
		self.assertEqual(logging.ERROR,  self.config.level)

	def test_set_level(self):
		self.config.level = logging.DEBUG
		self.assertEqual(logging.DEBUG,  self.config.level)
		self.config.level = None
		self.assertEqual(logging.ERROR,  self.config.level)


if __name__ == '__main__':
    unittest.main()

