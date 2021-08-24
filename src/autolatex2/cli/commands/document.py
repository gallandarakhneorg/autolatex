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

import os

from autolatex2.cli.commands.images import MakerAction as extended_maker_action
from autolatex2.make.maketool import AutoLaTeXMaker

import gettext
_T = gettext.gettext

# Extends MakerAction from images modules (alias extended_maker_action) in order
# to inherit the optional command line arguments from this super action.
class MakerAction(extended_maker_action):

	id = 'document'

	alias = 'gen_doc'

	help = _T('Performs all processing actions that are required to produce the PDF, DVI or Postscript. The actions set includes LaTeX, BibTeX, Makeindex, Dvips, etc.')

	def _add_command_cli_arguments(self,  action_parser, command):
		'''
		Callback for creating the CLI arguments (positional and optional).
		:param action_parser: The argparse object
		:param command: The description of the command.
		'''
		super()._add_command_cli_arguments(action_parser, command)
		#
		action_parser.add_argument('--nochdir', 
			action = 'store_true', 
			help=_T('Don\'t set the current directory of the application to document\'s root directory before the launch of the building process'))

	def run(self,  args) -> bool:
		'''
		Callback for running the command.
		:param args: the arguments.
		:return: True if the process could continue. False if an error occurred and the process should stop.
		'''
		#
		# DANGER: Do not call the super.run() function because it has not the expected behavior for the current command.
		#
		# Create the maker
		maker = self._internal_create_maker(args)
		self._internal_run_images(maker,  args)
		return self._internal_run_build(maker,  args)

	def _internal_run_images(self,  maker : AutoLaTeXMaker,  args):
		'''
		Run the internal behavior of the 'images' command.
		:param maker: the AutoLaTeX maker.
		:param args: the arguments.
		:return: the dict of images
		:rtype: dict
		'''
		if self.configuration.translators.is_translator_enable:
			return maker.run_translators(forceGeneration = args.force)
		return list()

	def _internal_run_build(self,  maker : AutoLaTeXMaker,  args) -> bool:
		'''
		Run the internal behavior of the 'images' command.
		:param maker: the AutoLaTeX maker.
		:param args: the arguments.
		:return: True to continue process. False to stop the process.
		'''
		ddir = self.configuration.documentDirectory
		if ddir and not args.nochdir:
			os.chdir(ddir)
		return maker.build()
