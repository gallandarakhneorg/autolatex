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

import os

from autolatex2.cli.main import AbstractMakerAction
from autolatex2.translator.translatorrepository import TranslatorRepository
from autolatex2.translator.translatorrunner import TranslatorRunner
from autolatex2.utils.extprint import eprint
import autolatex2.utils.utilfunctions as genutils

import gettext
_T = gettext.gettext

class MakerAction(AbstractMakerAction):

	id = 'showimages'

	help = _T('Display the filenames of the figures that are automatically generated')

	def _add_command_cli_arguments(self,  action_parser, command):
		'''
		Callback for creating the CLI arguments (positional and optional).
		:param action_parser: The argparse object
		:param command: The description of the command.
		'''
		output_group = action_parser.add_mutually_exclusive_group()

		output_group.add_argument('--changed',
			action='store_true',
			dest='showchangedimages', 
			help=_T('Show only the images for which the generated files are not up-to-date'))

		output_group.add_argument('--translators',
			action='store_true',
			dest='showimagetranslators', 
			help=_T('Show the names of the translators that is associated to each of the images'))

		output_group.add_argument('--valid',
			action='store_true',
			dest='showvalidimages', 
			help=_T('Show only the images for which the generated files are up-to-date'))


	def run(self,  args) -> bool:
		'''
		Callback for running the command.
		:param args: the arguments.
		:return: True to continue process. False to stop the process.
		'''
		# Create the translator repository
		repository = TranslatorRepository(self.configuration)
		# Create the runner of translators
		runner = TranslatorRunner(repository)
		# Detect the images
		runner.sync()
		images = runner.getSourceImages()
		# Show detect images
		ddir = self.configuration.documentDirectory
		image_list = dict()
		if ddir:
			for image in images:
				relpath = os.path.relpath(image,  ddir)
				abspath = genutils.abspath(image,  ddir)
				image_list[abspath] = relpath
		else:
			for image in images:
				relpath = os.path.relpath(image)
				abspath = os.path.abspath(image)
				image_list[abspath] = relpath
		
		if args.showvalidimages:
			self._show_valid_images(image_list,  runner)
		elif args.showchangedimages:
			self._show_changed_images(image_list,  runner)
		elif args.showimagetranslators:
			self._show_image_translators(image_list,  runner)
		else:
			self._show_all_images(image_list,  runner)
		return True

	def _show_all_images(self,  image_list,  runner):
		sorted_dict = {k: image_list[k] for k in sorted(image_list)}
		for abspath, relpath in sorted_dict.items():
			eprint(relpath)

	def _show_image_translators(self,  image_list,  runner):
		sorted_dict = {k: image_list[k] for k in sorted(image_list)}
		for abspath, relpath in sorted_dict.items():
			translator = runner.getTranslatorFor(abspath)
			if translator:
				eprint(_T("%s => %s") % (relpath, translator.name))

	def _show_changed_images(self,  image_list,  runner):
		sorted_dict = {k: image_list[k] for k in sorted(image_list)}
		for abspath, relpath in sorted_dict.items():
			if not self._is_valid_image(abspath,  runner):
				eprint(relpath)

	def _show_valid_images(self,  image_list,  runner):
		sorted_dict = {k: image_list[k] for k in sorted(image_list)}
		for abspath, relpath in sorted_dict.items():
			if self._is_valid_image(abspath,  runner):
				eprint(relpath)

	def _is_valid_image(self,  image,  runner) -> bool:
			inchange = genutils.getFileLastChange(image)
			target_files = runner.getTargetFiles(infile = image)
			if target_files:
				for target_file in target_files:
					outchange = genutils.getFileLastChange(target_file)
					if outchange is None or outchange < inchange:
						return False
				return True
			else:
				return False
