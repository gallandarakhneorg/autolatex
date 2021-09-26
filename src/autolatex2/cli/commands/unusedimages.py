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
from autolatex2.tex.imageinclusions import ImageInclusions
from autolatex2.make.maketool import AutoLaTeXMaker
from autolatex2.utils.extprint import eprint
import autolatex2.utils.utilfunctions as genutils

import gettext
_T = gettext.gettext

class MakerAction(AbstractMakerAction):

	id = 'unusedimages'

	help = _T('Display (or remove) the figures that are inside the document folder and not included into the document')

	IMAGE_FORMATS = ['.png', '.jpeg', '.jpg', '.eps', '.ps', '.pdf', '.gif', '.bmp', '.pdftex_t', '.pstex_t', '.pdf_tex', '.ps_tex']

	def _add_command_cli_arguments(self,  action_parser, command):
		'''
		Callback for creating the CLI arguments (positional and optional).
		:param action_parser: The argparse object
		:param command: The description of the command.
		'''
		action_parser.add_argument('--delete', 
			action='store_true', 
			help=_T('Delete the unused figures instead of simply listing them'))

	def _is_picture(self,  image : str) -> bool:
		limage = image.lower()
		for ext in MakerAction.IMAGE_FORMATS:
			if (limage.endswith(ext)):
				return True
		return False

	def _is_auto_figure_folder(self,  name : str) -> bool:
		# Smooth out relative path names, note: if you are concerned about symbolic links, you should use os.path.realpath too
		sname = os.path.abspath(name)
		for root in self.configuration.translators.imagePaths:
			parent = os.path.abspath(root)
			# Compare the common path of the parent and child path with the common path of just the parent path.
			# Using the commonpath method on just the parent path will regularise the path name in the same way
			# as the comparison that deals with both paths, removing any trailing path separator
			if os.path.commonpath([parent]) == os.path.commonpath([parent, sname]):
				return True
		return False

	def _get_manually_given_images(self,  auto_images : set) -> set:
		'''
		Replies the list of images that are not automatically generated.
		:param auto_images: The list of images that are generated thant not provided manually.
		:type auto_images: set
		:return: The set of image filenames
		:rtype: set
		'''
		manual_images = set()
		for root, dirs, files in os.walk(self.configuration.documentDirectory):
			for basename in files:
				full_name = os.path.join(root,  basename)
				if self._is_picture(full_name) and full_name not in auto_images:
					manual_images.add(full_name)
		return manual_images

	def _get_auto_images(self) -> set:
		'''
		Replies the list of images that are automatically generated.
		:return: The set of image filenames
		:rtype: set
		'''
		# Explore the auto-generated images
		repository = TranslatorRepository(self.configuration)
		# Create the runner of translators
		runner = TranslatorRunner(repository)
		# Detect the images
		runner.sync()
		# Detect the target images
		auto_images = runner.getSourceImages()
		target_images = set()
		for image in auto_images:
			targets = runner.getTargetFiles(infile = image)
			target_images.update(targets)
		return target_images

	def run(self,  args) -> bool:
		'''
		Callback for running the command.
		:param args: the arguments.
		:return: True to continue process. False to stop the process.
		'''
		# Explore the auto-generated images
		auto_images = self._get_auto_images()

		# Explore the folders
		manual_images = self._get_manually_given_images(auto_images)
		
		# Parse the TeX
		maker = AutoLaTeXMaker.create(self.configuration)

		included_images = set()
		for root_file in maker.rootFiles:
			parser = ImageInclusions(filename = root_file)
			if not parser.run():
				return False
			images = parser.get_included_figures()
			included_images.update(images)
		
		# Compute the not-included figures
		not_included_images = manual_images.difference(included_images)
		
		# Do the action
		ddir = self.configuration.documentDirectory
		for image_file in not_included_images:
			relpath = os.path.relpath(image_file,  ddir)
			abspath = genutils.abspath(image_file,  ddir)
			eprint(relpath)
			if args.delete:
				#eprint("> " + abspath)
				genutils.unlink(abspath)

		return True

