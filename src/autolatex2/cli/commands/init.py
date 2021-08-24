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

import logging
import os
import sys
import textwrap


from autolatex2.config.configobj import Config
from autolatex2.config.configwriter import OldStyleConfigWriter
from autolatex2.cli.main import AbstractMakerAction

import gettext
_T = gettext.gettext

class MakerAction(AbstractMakerAction):

	id = 'init'

	help = _T('Create an empty LaTeX document that is following a standard folder structure suitable for AutoLaTeX')

	def _add_command_cli_arguments(self,  action_parser, command):
		'''
		Callback for creating the CLI arguments (positional and optional).
		:param action_parser: The argparse object
		:param command: The description of the command.
		'''
		action_parser.add_argument('--force', 
			action = 'store_true', 
			help=_T('Force to overwrite any existing file'))
		action_parser.add_argument('--out', 
			action = 'store', 
			default = None, 
			type=str, 
			help=_T('Specify the output directory for creating the project structure'))

	def run(self,  args) -> bool:
		'''
		Callback for running the command.
		:param args: the arguments.
		:return: True to continue process. False to stop the process.
		'''
		if args.out:
			dout = os.path.abspath(args.out)
		else:
			dout = os.getcwd()

		cfg = Config()

		tex_file = os.path.join(dout,  'main.tex')
		if os.path.isfile(tex_file) and not args.force:
			logging.error(_T("TeX file already exists: %s") % (tex_file))
			sys.exit(255)
		cfg.documentDirectory = os.path.dirname(tex_file)
		cfg.documentFilename= os.path.basename(tex_file)
		tex_file_content = textwrap.dedent('''\
		\\documentclass{article}
		\\begin{document}
		\\end{document}
		''')

		rimgdir = os.path.join('images',  'auto')
		imgdir = os.path.join(dout,  rimgdir)
		cfg.translators.addImagePath(imgdir)

		cfg_file = cfg.makeDocumentConfigFilename(dout)
		if os.path.isfile(cfg_file) and not args.force:
			logging.error(_T("Configuration file already exists: %s") % (cfg_file))
			sys.exit(255)
	
		gitignore_file = os.path.join(dout,  '.gitignore')
		excl1 = os.path.join('*',  rimgdir,  '*.pdf')
		excl2 = os.path.join('*',  rimgdir,  '*', '*.pdf')
		gitignore_file_content = textwrap.dedent('''\
			.autolatex_stamp
			*.aux
			*.log
			*.nav
			*.out
			*.pdf
			*.snm
			*.synctex
			*.synctex.gz
			*.toc
			*.vrb
			*.bbl
			*.blg
			%s
			%s
			*.pdftex_t
		''') % (excl1,  excl2)

		logging.info(_T("Creating document structure in %s") % (dout))
		try:
			# Create the folders
			os.makedirs(imgdir, exist_ok=True)
			# Create the TeX file
			with open(tex_file,  'w') as file:
				file.write(tex_file_content)
			# Git ignore
			if os.path.isfile(gitignore_file):
				logging.warning(_T('Ignore file that already exists: %s') % (gitignore_file))
			else:
				with open(gitignore_file,  'w') as file:
					file.write(gitignore_file_content)
			# Create the configuration file
			writer = OldStyleConfigWriter()
			writer.write(cfg_file,  cfg)
		except BaseException as ex:
			logging.error(str(ex))
			return False
		return True
