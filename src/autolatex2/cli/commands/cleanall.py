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

from autolatex2.cli.commands.clean import MakerAction as extended_maker_action
from autolatex2.make.maketool import AutoLaTeXMaker

import gettext
_T = gettext.gettext

class MakerAction(extended_maker_action):

	id = 'cleanall'
	
	alias = ['mrproper']

	help = _T('Extend the \'clean\' command by removing the backup files and the automatically generated images')

	MORE_CLEANABLE_FILE_EXTENSIONS = [
		'~',
		'.back',
		'.backup',
		'.bak',
	]

	def run(self,  args) -> bool:
		'''
		Callback for running the command.
		:param args: the arguments.
		:return: True if the process could continue. False if an error occurred and the process should stop.
		'''
		# Remove the tamporary files
		if not super().run(args):
			return False
		# Remove additional files
		maker = AutoLaTeXMaker.create(self.configuration)
		# Prepare used-defined list of deletable files
		clean_files = self.configuration.clean.cleanallFiles
		abs_clean_files = list()
		bn_clean_files = list()
		for file in clean_files:
			if os.sep in file:
				abs_clean_files.append(file)
			else:
				bn_clean_files.append(file)
		for root_file in maker.rootFiles:
			root_dir = os.path.dirname(root_file)
			if args.norecursive:
				root = os.path.dirname(root_file)
				for filename in os.listdir(root):
					abs_filename = os.path.join(root,  filename)
					if self._is_deletable_more(root,  root_file, abs_filename):
						self._delete_file(abs_filename,  args.simulate)
					elif self._is_deletable_shell(root,  root_file, abs_filename,  filename,  abs_clean_files,  bn_clean_files):
						self._delete_file(abs_filename,  args.simulate)
			else:
				for root, dirs, files in os.walk(os.path.dirname(root_file)):
					for filename in files:
						abs_filename = os.path.join(root,  filename)
						if root == root_dir and self._is_deletable_more(root,  root_file, abs_filename):
							self._delete_file(abs_filename,  args.simulate)
						elif self._is_deletable_shell(root,  root_file, abs_filename,  filename,  abs_clean_files,  bn_clean_files):
							self._delete_file(abs_filename,  args.simulate)
		return True

	def _is_deletable_more(self,  root_dir : str,  tex_filename : str,  filename : str) -> bool:
		'''
		Replies if the given filename is for a deletable file anywhere.
		'''
		if os.name == 'nt':
			fnl = filename.lower()
			for ext in MakerAction.MORE_CLEANABLE_FILE_EXTENSIONS:
				if fnl.endswith(ext):
					return True
		else:
			for ext in MakerAction.MORE_CLEANABLE_FILE_EXTENSIONS:
				if filename.endswith(ext):
					return True
		return False
