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

from autolatex2.tex.texparser import *

class TestParameter(unittest.TestCase):

	def setUp(self):
		logging.getLogger().setLevel(logging.CRITICAL)
		self.parameter = Parameter()



	def test_expandable_0(self):
		self.assertTrue(self.parameter.expandable)

	def test_expandable_1(self):
		self.parameter.expandable = False
		self.assertFalse(self.parameter.expandable)

	def test_value_0(self):
		self.assertIsNone(self.parameter.value)

	def test_value_1(self):
		self.parameter.value = 'abc'
		self.assertIsNotNone(self.parameter.value)
		self.assertEqual('abc', self.parameter.value)



if __name__ == '__main__':
    unittest.main()

