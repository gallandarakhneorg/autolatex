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
import tempfile
import os
import shutil

from autolatex2.cli.autolatex import AutoLaTeXMain
from autolatex2.cli.main import AutoLaTeXExceptionExiter

class TestBug97(unittest.TestCase):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.__output_directory = None
		self.__action = None

	def __createWorkingDirectory(self) -> str:
		directory = tempfile.mkdtemp()
		with open(os.path.join(directory, "pack1.sty"), 'w') as f:
			f.write("\\NeedsTeXFormat{LaTeX2e}[1995/12/01]\n")
			f.write("\\ProvidesPackage{pack1}[2021/09/11]\n")
			f.write("\\RequirePackage{pack2}\n")
			f.write("\def\\firstpackage{}\n")
			f.flush()
		with open(os.path.join(directory, "pack2.sty"), 'w') as f:
			f.write("\\NeedsTeXFormat{LaTeX2e}[1995/12/01]\n")
			f.write("\\ProvidesPackage{pack2}[2021/09/11]\n")
			f.write("\\RequirePackage{pack3}\n")
			f.write("\def\\secondpackage{}\n")
			f.flush()
		with open(os.path.join(directory, "pack3.sty"), 'w') as f:
			f.write("\\NeedsTeXFormat{LaTeX2e}[1995/12/01]\n")
			f.write("\\ProvidesPackage{pack2}[2021/09/11]\n")
			f.write("\def\\thirdpackage{}\n")
			f.flush()
		with open(os.path.join(directory, "main.tex"), 'w') as f:
			f.write("\\documentclass{article}\n")
			f.write("\\usepackage{pack1}\n")
			f.write("\\begin{document}\n")
			f.write("This is a text\\thirdpackage\n")
			f.write("\\end{document}\n")
			f.flush()
		return directory

	def setUp(self):
		logging.getLogger().setLevel(logging.CRITICAL)
		self.__output_directory = self.__createWorkingDirectory()
		self.__action = AutoLaTeXMain(read_system_config = False,  read_user_config = False,  args = ['--noauto', '--directory',  self.__output_directory,  'makeflat'],  exiter = AutoLaTeXExceptionExiter())

	def tearDown(self):
		if self.__output_directory is not None and os.path.isdir(self.__output_directory):
			shutil.rmtree(self.__output_directory)
		self.__output_directory = None
		self.__action = None

	def test_runMakeflat(self):
		self.__action.run()





if __name__ == '__main__':
    unittest.main()

