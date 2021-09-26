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

import logging
import os
import shutil

from autolatex2.cli.commands.document import MakerAction as extended_maker_action
from autolatex2.tex.flattener import Flattener
import autolatex2.utils.utilfunctions as genutils
from autolatex2.make.maketool import AutoLaTeXMaker

import gettext
_T = gettext.gettext

# Extends MakerAction from document module (alias extended_maker_action) in order
# to inherit from this super action.
class MakerAction(extended_maker_action):

	id = 'makeflat'
	
	alias = ['preparepublish']

	help = _T('Create a version of the document inside the specified directory (by default \'flat_version\') in which there is a single TeX file, and '
					+ 'all the other files are inside the same directory of the TeX file. This action is helpful to create a version of the document that may '
					+ 'be directly upload on online publisher sites (such as Elsevier). This command runs \'document\' before creating the new version of the '
					+ 'document. Also, the bibliography entries are extracted from the BibTeX files to be inlined into the generated TeX file')

	def _add_command_cli_arguments(self,  action_parser, command):
		'''
		Callback for creating the CLI arguments (positional and optional).
		:param action_parser: The argparse object
		:param command: The description of the command.
		'''
		super()._add_command_cli_arguments(action_parser, command)

		action_parser.add_argument('--externalbiblio', 
			action='store_true', 
			help=_T('Force the use of an external BibTeX file (i.e. \'.bib\' file) instead of inlining the bibliography database inside the TeX file'))

		action_parser.add_argument('--out', 
			default='flat_version', 
			metavar=('DIRECTORY'), 
			help=_T('Specify the output directory in which the flat version is created. By default, the name of the directory is \'flat_version\''))

	def run(self,  args) -> bool:
		'''
		Callback for running the command.
		:param args: the arguments.
		:return: True if the process could continue. False if an error occurred and the process should stop.
		'''
		# Run the building behavior
		if not super().run(args):
			return False

		maker = AutoLaTeXMaker.create(self.configuration)

		for root_file in maker.rootFiles:
			root_dir = os.path.dirname(root_file)
			# Output
			output_dir = genutils.abspath(args.out, root_dir)
			
			logging.debug(_T("Generating flat version into: %s") % (output_dir))

			# Delete the output directory
			try:
				if os.path.isdir(output_dir):
					shutil.rmtree(output_dir)
			except:
				pass

			# Create the flattening tool
			flattener = Flattener(filename = root_file,  outputDirectory = output_dir)
			flattener.use_biblio = args.externalbiblio
			if not flattener.run():
				return False
		return True
