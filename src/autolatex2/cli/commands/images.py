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

from autolatex2.cli.main import AbstractMakerAction
from autolatex2.make.maketool import AutoLaTeXMaker

import gettext
_T = gettext.gettext

class MakerAction(AbstractMakerAction):

	id = 'images'

	help = _T('Performs the automatic generation of the figures based on the calls to the enabled translators')

	def _add_command_cli_arguments(self,  action_parser, command):
		'''
		Callback for creating the CLI arguments (positional and optional).
		:param action_parser: The argparse object
		:param command: The description of the command.
		'''
		action_parser.add_argument('--force', 
			action = 'store_true', 
			help=_T('Force the generation of the images even if the source image is not more recent than the generated image'))

	def run(self,  args) -> bool:
		'''
		Callback for running the command.
		:param args: the arguments.
		:return: True to continue process. False to stop the process.
		'''
		maker = self._internal_create_maker(args)
		generated_images = self._internal_run_images(maker,  args)
		# Output the result of the command
		nb = 0
		if generated_images:
			for source,  target in generated_images.items():
				if target:
					nb = nb + 1
		logging.info(_T("%d images were generated") % (nb))
		return True

	def _internal_create_maker(self,  args) -> AutoLaTeXMaker:
		'''
		Create the maker.
		:param args: the arguments.
		:return: the maker
		:rtype: AutoLaTeXMaker
		'''
		return AutoLaTeXMaker.create(self.configuration)

	def _internal_run_images(self,  maker : AutoLaTeXMaker,  args):
		'''
		Run the internal behavior of the 'images' command.
		:param maker: the AutoLaTeX maker.
		:param args: the arguments.
		:return: the dict of images
		:rtype: dict
		'''
		return maker.run_translators(forceGeneration = args.force)
