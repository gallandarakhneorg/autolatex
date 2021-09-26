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
import re
import fnmatch

from autolatex2.cli.main import AbstractMakerAction
from autolatex2.make.maketool import AutoLaTeXMaker
import autolatex2.utils.utilfunctions as genutils
import autolatex2.tex.utils as texutils

import gettext
_T = gettext.gettext

class MakerAction(AbstractMakerAction):

	id = 'clean'

	help = _T('Clean the current working directory by removing all LaTeX temp files and other temp files that are created during the processing of the document')

	CLEANABLE_FILE_EXTENSIONS = [
		'.aux',
		'.bcf',
		'.bbl',
		'.blg',
		'.bmt',
		'.brf',
		'.cb', 
		'.fls',
		'.glg',
		'.glo',
		'.gls',
		'.idx',
		'.ilg',
		'.ind', 
		'.lbl',
		'.loa',
		'.loc',
		'.loe',
		'.lof', 
		'.log', 
		'.lom', 
		'.los', 
		'.lot',
		'.maf',
		'.mtc',
		'.mtf',
		'.mtl',
		'.nav',
		'.out', 
		'.run.xml', 
		'.snm',
		'.soc',
		'.spl',
		'.thlodef',
		'.tmp', 
		'.toc', 
		'.vrb',
		'.xdy', 
	]

	CLEANABLE_FILE_PATTERNS = [
		'\\.goutputstream-.+',
		'\\.mtc[0-9]+',
		'\\.mtf[0-9]+',
		'\\.mtl[0-9]+',
	]

	MORE_CLEANABLE_FILE_EXTENSIONS = [
		'~',
		'.back',
		'.backup',
		'.bak',
	]

	def __init__(self):
		super().__init__()
		self.__nb_deletions = 0

	def _add_command_cli_arguments(self,  action_parser, command):
		'''
		Callback for creating the CLI arguments (positional and optional).
		:param action_parser: The argparse object
		:param command: The description of the command.
		'''
		action_parser.add_argument('--nochdir', 
			action = 'store_true', 
			help=_T('Don\'t set the current directory of the application to document\'s root directory before the launch of the building process'))

		action_parser.add_argument('--norecursive', 
			action = 'store_true', 
			help=_T('Disable cleaning of the subfolders'))

		action_parser.add_argument('--simulate', 
			action = 'store_true', 
			help=_T('Simulate the removal of the files, i.e. the files are not removed from the disk'))

		if command.name == 'clean':
			action_parser.add_argument('--all', 
				action = 'store_true', 
				help=_T('If specified, the cleaning command behaves as the command \'cleanall\''))

	def __callback_run_cleanall(self,  args) -> bool:
		return False

	def run(self,  args) -> bool:
		'''
		Callback for running the command.
		:param args: the arguments.
		:return: True if the process could continue. False if an error occurred and the process should stop.
		'''
		self.__nb_deletions = 0
		if not self.run_clean_command(args):
			return False
		if (args.all):
			if not self.run_cleanall_command(args):
				return False
		self._show_deletions_message(args)
		return True

	def _show_deletions_message(self,  args):
		'''
		Show the conclusion message.
		:param args: The CLI arguments.
		:type args: argparse object
		'''
		if self.__nb_deletions > 1:
			if args.simulate:
				msg = _T("%d files were selected as deletion candidates") % (self.__nb_deletions)
			else:
				msg = _T("%d files were deleted") % (self.__nb_deletions)
		else:
			if args.simulate:
				msg = _T("%d file was selected as deletion candidate") % (self.__nb_deletions)
			else:
				msg = _T("%d file was deleted") % (self.__nb_deletions)
		logging.info(msg)

	def run_clean_command(self,  args) -> bool:
		'''
		Run the command 'clean'.
		:param args: the arguments.
		:return: True if the process could continue. False if an error occurred and the process should stop.
		'''
		ddir = self.configuration.documentDirectory	
		if ddir and not args.nochdir:
			os.chdir(ddir)
		maker = AutoLaTeXMaker.create(self.configuration)
		# Prepare used-defined list of deletable files
		clean_files = self.configuration.clean.cleanFiles
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
					if self._is_deletable_in_root_folder_only(root,  root_file, abs_filename):
						self._delete_file(abs_filename,  args.simulate)
					elif self._is_deletable(root,  root_file, abs_filename):
						self._delete_file(abs_filename,  args.simulate)
					elif self._is_deletable_shell(root,  root_file, abs_filename,  filename,  abs_clean_files,  bn_clean_files):
						self._delete_file(abs_filename,  args.simulate)
			else:
				for root, dirs, files in os.walk(os.path.dirname(root_file)):
					for filename in files:
						abs_filename = os.path.join(root,  filename)
						if root == root_dir and self._is_deletable_in_root_folder_only(root,  root_file, abs_filename):
							self._delete_file(abs_filename,  args.simulate)
						elif self._is_deletable(root,  root_file, abs_filename):
							self._delete_file(abs_filename,  args.simulate)
						elif self._is_deletable_shell(root,  root_file, abs_filename,  filename,  abs_clean_files,  bn_clean_files):
							self._delete_file(abs_filename,  args.simulate)
		return True

	def run_cleanall_command(self,  args) -> bool:
		'''
		Run the command 'cleanall' or '--all' optional argument.
		:param args: the arguments.
		:return: True if the process could continue. False if an error occurred and the process should stop.
		'''
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

	def _delete_file(self,  filename : str,  simulate : bool):
		if simulate:
			msg = _T("Selecting: %s") % (filename)
		else:
			msg = _T("Deleting: %s") % (filename)
		logging.info(msg)
		if not simulate:
			genutils.unlink(filename)
		self.__nb_deletions = self.__nb_deletions + 1

	def _is_deletable_in_root_folder_only(self,  root_dir : str,  tex_filename : str,  filename : str) -> bool:
		'''
		Replies if the given filename is for a deletable file in the root folder.
		'''
		basename = genutils.basename2(os.path.join(root_dir,  tex_filename),  texutils.getTeXFileExtensions())
		candidates = [
			os.path.join(root_dir, '.autolatex_stamp'),
			os.path.join(root_dir, 'autolatex_stamp'),
			os.path.join(root_dir, 'autolatex_exec_stderr.log'),  # For old version of AutoLaTeX
			os.path.join(root_dir, 'autolatex_exec_stdout.log'), # For old version of AutoLaTeX
			os.path.join(root_dir, 'autolatex_exec_stdin.log'), # For old version of AutoLaTeX
			os.path.join(root_dir, 'autolatex_autogenerated.tex'),
			basename + ".pdf",
			basename + ".dvi",
			basename + ".xdvi",
			basename + ".xdv",
			basename + ".ps",
			basename + ".synctex.gz",
			basename + ".synctex",
		]
		return filename in candidates

	def _is_deletable(self,  root_dir : str,  tex_filename : str,  filename : str) -> bool:
		'''
		Replies if the given filename is for a deletable file anywhere.
		'''
		if os.name == 'nt':
			fnl = filename.lower()
			for ext in MakerAction.CLEANABLE_FILE_EXTENSIONS:
				if fnl.endswith(ext):
					return True
			for ext in MakerAction.CLEANABLE_FILE_EXTENSIONS:
				if re.match(ext + '$',  fnl):
					return True
		else:
			for ext in MakerAction.CLEANABLE_FILE_EXTENSIONS:
				if filename.endswith(ext):
					return True
			for ext in MakerAction.CLEANABLE_FILE_PATTERNS:
				if re.match(ext + '$',  filename):
					return True
		return False

	def _is_deletable_shell(self,  root_dir : str,  tex_filename : str,  filename : str,  basename : str,  absolute_shell_patterns : list,  basename_shell_patterns : list) -> bool:
		'''
		Replies if the given filename Shell pattern is for a deletable file anywhere.
		'''
		for pattern in absolute_shell_patterns:
			if fnmatch.fnmatch(filename,  pattern):
				return True
		for pattern in basename_shell_patterns:
			if fnmatch.fnmatch(basename,  pattern):
				return True
		return False
