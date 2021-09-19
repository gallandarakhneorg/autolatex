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
import glob

from autolatex2.cli.autolatex import AutoLaTeXMain
from autolatex2.cli.main import AutoLaTeXExceptionExiter
import autolatex2.utils.utilfunctions as genutils

class TestBug109(unittest.TestCase):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.__output_directory = None
		self.__action = None

	def setUp(self):
		logging.getLogger().setLevel(logging.CRITICAL)
		self.__output_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)),  'test')
		self.__action = AutoLaTeXMain(read_system_config = False,  read_user_config = False,  args = ['--noauto', '--directory',  self.__output_directory],  exiter = AutoLaTeXExceptionExiter())

	def tearDown(self):
		if self.__output_directory is not None and os.path.isdir(self.__output_directory):
			for file in glob.glob(os.path.join(self.__output_directory,  '*')):
				if not file.endswith('main.tex') and not file.endswith('biblio.bib'):
					genutils.unlink(file)
		self.__output_directory = None
		self.__action = None

	def test_runMakeflat(self):
		self.__action.run()





if __name__ == '__main__':
    unittest.main()

