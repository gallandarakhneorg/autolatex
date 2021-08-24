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
import argparse

from autolatex2.cli.main import AbstractAutoLaTeXMain
from autolatex2.utils.extlogging import ensureAutoLaTeXLoggingLevels

import gettext
_T = gettext.gettext


class AutoLaTeXMain(AbstractAutoLaTeXMain):

	def __init__(self,  read_system_config : bool = True,  read_user_config : bool = True):
		'''
		Constructor.
		:param read_system_config: Indicates if the system-level configuration must be read. Default is True.
		:type read_system_config: bool
		:param read_user_config: Indicates if the user-level configuration must be read. Default is True.
		:type read_user_config: bool
		'''
		ensureAutoLaTeXLoggingLevels()
		super().__init__(read_system_config,  read_user_config)
		self.__commands = dict()

	def add_cli_options(self,  cli_parser : object):
		'''
		Add the definition of the application CLI options.
		:param cli_parser: the CLI parser
		'''
		async_group = cli_parser.add_argument_group(_T('asynchronous behavior optional arguments'))

		# --view
		# --noview
		class ViewAction(argparse.Action):
			def __call__(actionself, parser, namespace, value, option_string=None):
				self.configuration.view.view = actionself.const

		view_group = async_group.add_mutually_exclusive_group()

		view_group.add_argument('--view',
			action = ViewAction, 
			const=True, 
			nargs=0, 
			help=_T('Enable the document viewer at the end of the compilation'))

		view_group.add_argument('--noview',
			action = ViewAction, 
			const=False, 
			nargs=0, 
			help=_T('Disable the document viewer at the end of the compilation'))

		# --asyncview
		# --noasyncview
		asyncview_group = async_group.add_mutually_exclusive_group()

		class AsyncviewAction(argparse.Action):
			def __call__(actionself, parser, namespace, value, option_string=None):
				self.configuration.view.asyncview = actionself.const

		asyncview_group.add_argument('--asyncview',
			action=AsyncviewAction,
			const=True, 
			nargs=0, 
			help=_T('Enable the asynchronous launching of the viewer'))

		asyncview_group.add_argument('--noasyncview',
			action=AsyncviewAction,
			const=False, 
			nargs=0, 
			help=_T('Disable the asynchronous launching of the viewer'))

		# --continuous
		# --nocontinuous
		continuous_group = async_group.add_mutually_exclusive_group()

		class ContinuousAction(argparse.Action):
			def __call__(actionself, parser, namespace, value, option_string=None):
				self.configuration.infiniteLoop = True
				if value:
					try:
						self.configuration.infiniteLoopDelay = int(value)
					except:
						pass
		continuous_group.add_argument('--continuous',
			action = ContinuousAction, 
			nargs = '?', 
			metavar=('SECONDS'), 
			help=_T('Do not stop AutoLaTeX, and continually do the action(s) given as parameter(s). If SECONDS is specified, it is the delay to wait for between two runs of AutoLaTeX'))

		class NocontinuousAction(argparse.Action):
			def __call__(actionself, parser, namespace, value, option_string=None):
				self.configuration.infiniteLoop = False
		continuous_group.add_argument('--nocontinuous', 
			action=NocontinuousAction, 
			nargs = 0, 
			help=_T('Disable continuous execution of AutoLaTeX'))

	def add_cli_positional_arguments(self,  cli_parser : object):
		'''
		Add the definition of the application CLI positional arguments.
		:param parser: the CLI parser
		'''
		self.__commands = self._build_command_dict('autolatex2.cli.commands')
		if self.__commands:
			self._create_cli_arguments_for_commands(commands = self.__commands,  title = _T("commands"),  help = _T('Command to be run by autolatex, by default \'all\'. Available commands are:'))

	def _pre_run_program(self) -> list:
		'''
		Run the behavior of the main program before the specific behavior.
		:return: the CLI args that are not consumed by argparse library.
		:rtype: list
		'''
		args = super()._pre_run_program()

		if not self.configuration.documentFilename:
			self.configuration.documentFilename = self.__detect_tex_file(self.configuration.documentDirectory)
		
		return args

	def __detect_tex_file(self,  directory : str):
		files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)) and f.endswith('.tex')]
		length = len(files)
		if length <= 0:
			logging.error(_T("Unable to find a TeX file to compile in: %s") % (directory))
			sys.exit(255)
		else:
			file = files[0]
			if length > 1:
				logging.warning(_T("Too much TeX files in: %s") % (directory))
				logging.warning(_T("Select the TeX file: %s") % (file))
			return file

	def _run_program(self,  args : list):
		'''
		Run the specific behavior.
		:param args: the CLI arguments that are not consumed by the argparse library.
		:type args: list
		'''
		# If no command is given, the 'all' is assumed.
		self._ensure_command_function(args,  self.__commands,  'all')
		self._execute_commands(args)



if __name__ == '__main__':
	main_program = AutoLaTeXMain()
	main_program.run()
