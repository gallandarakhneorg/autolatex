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

from autolatex2.cli.main import AbstractMakerAction
from autolatex2.translator.translatorrepository import TranslatorRepository
from autolatex2.translator.translatorrunner import TranslatorRunner
from autolatex2.utils.extprint import eprint

import gettext
_T = gettext.gettext

class MakerAction(AbstractMakerAction):

	id = 'showimages'

	help = _T('Display the filenames of the figures that are automatically generated')

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
		if ddir:
			for image in images:
				relpath = os.path.relpath(image,  ddir)
				eprint(relpath)
		else:
			for image in images:
				relpath = os.path.relpath(image)
				eprint(relpath)
		return True

