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

'''
Main program implementation for AutoLaTeX.
'''

import logging
import argparse
import sys
import os
import platform
import textwrap
from abc import ABC,  abstractmethod

import autolatex2.utils.utilfunctions as genutils
from autolatex2.utils.extlogging import ensureAutoLaTeXLoggingLevels
from autolatex2.utils.extlogging import LogLevel
from autolatex2.config.configobj import Config
from autolatex2.config.configreader import OldStyleConfigReader
from autolatex2.translator.translatorobj import TranslatorLevel
import autolatex2.utils.extprint as eprintpkg

import gettext
_T = gettext.gettext

SUPPRESS = '==SUPPRESS=='

class AutoLaTeXExiter(object):
	'''
	Callback that is invoked when AutoLaTeX should be terminated. This callback call the system exit instructions.
	'''
	def exitOnFailure(self):
		sys.exit(255)
	def exitOnException(self,  exception):
		sys.exit(255)
	def exitOnSuccess(self):
		sys.exit(0)

class AutoLaTeXExceptionExiter(object):
	'''
	Callback that is invoked when AutoLaTeX should be terminated. This callback generates an exception on failure.
	'''
	def exitOnFailure(self):
		raise Exception()
	def exitOnException(self,  exception):
		raise exception
	def exitOnSuccess(self):
		pass

class AutoLaTeXCommand(object):
	'''
	Command to be run that is launched by the user of AutoLaTeX.
	'''
	def __init__(self,  name : str,  type,  help : str,  alias = None):
		'''
		Constructor.
		:param name: The name of the command.
		:type name: str
		:param type: The type of action.
		:type type: class
		:param help: The help text.
		:type help: str
		:param alias: The alias for the command name.
		:type alias: str or list
		'''
		ensureAutoLaTeXLoggingLevels()
		self.name = name
		self.creator_type = type
		self.help = help
		self.__instance = None
		if alias is None:
			self.aliases = list()
		elif isinstance(alias,  list):
			self.aliases = alias
		else:
			self.aliases = list([str(alias)])

	@property
	def instance(self) -> object:
		if self.__instance is None:
			self.__instance = self.creator_type()
		return self.__instance



class AbstractMakerAction(ABC):
	'''
	Abstract implementation of a maker action/command.
	'''

	def __init__(self):
		self.__configuration = None

	def _add_command_cli_arguments(self,  action_parser, command):
		'''
		Callback for creating the CLI arguments (positional and optional).
		:param action_parser: The argparse object
		:param command: The description of the command.
		'''
		pass

	def register_command(self,  action_parser, command, configuration : Config):
		'''
		Callback for creating the CLI arguments (positional and optional).
		:param action_parser: The argparse object
		:param command: The description of the command.
		:param configuration: The configuration instance.
		'''
		self.__configuration = configuration
		if command.aliases:
			parser_cli = action_parser.add_parser(command.name, help = command.help,  aliases = command.aliases)
		else:
			parser_cli = action_parser.add_parser(command.name, help = command.help)
		parser_cli.set_defaults(__command_callback_func=self.run)
		self._add_command_cli_arguments(parser_cli,  command)

	@property
	def configuration(self) -> Config:
		return self.__configuration

	def run(self,  args) -> bool:
		'''
		Callback for running the command.
		:param args: the arguments.
		:return: True if the process could continue. False if an error occurred and the process should stop.
		'''
		return True



class AbstractAutoLaTeXMain(ABC):
	'''
	Main program implementation for AutoLaTeX.
	'''

	def __init__(self,  read_system_config : bool = True,  read_user_config : bool = True, args : list = None,  exiter : AutoLaTeXExiter = None):
		'''
		Constructor.
		:param read_system_config: Indicates if the system-level configuration must be read. Default is True.
		:type read_system_config: bool
		:param read_user_config: Indicates if the user-level configuration must be read. Default is True.
		:type read_user_config: bool
		:param args: List of command line arguments. If it is None, the system args are used.
		:type args: list
		:param exiter: The instance of the object that is called when AutoLaTeX should stop.
		:type exister: AutoLaTeXExiter
		'''
		self.__initial_argv = args
		self.__read_document_configuration = True
		if exiter:
			self.__exiter = exiter
		else:
			self.__exiter = AutoLaTeXExiter()

		# Create the AutoLaTeX configuration object
		self.configuration = Config()

		# Initialization of the logging system (must be after configuration creation)
		self.__logging_handler = None
		self._init_logging_system()
		
		# Initialization that depends on the script itself
		script_launchname = os.path.basename(os.sys.argv[0])
		(script_path,  script_ext) = os.path.splitext(os.sys.argv[0])
		script_name = os.path.basename(script_path)
		self.configuration.name = script_name
		self.configuration.launchName = script_launchname

		# Read the configuration from the system
		config_reader = OldStyleConfigReader()
		if read_system_config:
			config_reader.readSystemConfigSafely(self.configuration)

		# Read the configuration from the user home
		if read_user_config:
			config_reader.readUserConfigSafely(self.configuration)
		
		# Create the CLI parser
		self._cli_parser = self._create_cli_parser(name = self.configuration.name, version = self.configuration.version,  epilog = self._build_help_epilog())

	def _build_command_dict(self,  package_name) -> dict:
		'''
		Build the dictionnary that maps the command's names to AutoLaTeXCommand.
		:param package_name: The name of the package to explore.
		:type package_name: str
		:return: the dict of the commands.
		:rtype: dict
		'''
		execEnv = {
			'modules': None, 
		}
		exec("import " + package_name + "\nmodules = " + package_name + ".__all__",  None, execEnv)
		modules = execEnv['modules']
		ids = dict()
		for module in modules:
			execEnv = {
				'id': None, 
				'alias': None, 
				'type': None, 
				'help': None, 
			}
			cmd = textwrap.dedent('''\
						from %s.%s import MakerAction
						type = MakerAction
						id = MakerAction.id
						help = MakerAction.help
						try:
							alias = MakerAction.alias
						except:
							alias = None
			''') % (package_name,  module)
			exec(cmd,  None, execEnv)
			id = execEnv['id']
			ids[id] = AutoLaTeXCommand(name=id,  type=execEnv['type'],  help=execEnv['help'],  alias=execEnv['alias'])
		return ids

	def _create_cli_arguments_for_commands(self,  commands : dict,  title : str,  help : str,  metavar : str = 'COMMAND'):
		'''
		Create CLI arguments for the given commands.
		:param commands: the pairs "command id"-"command instance".
		:type commands: dict
		:param title: The title of the command set.
		:type title: str
		:param help: The help description of the command set.
		:type help: str
		:param metavar: The name of the command set in the help. Default is: COMMAND.
		:type metavar: str
		'''
		subparsers = self.cli_parser.add_subparsers(title = title,  metavar=(metavar),  help = help)
		for id,  command in commands.items():
			command.instance.register_command(action_parser=subparsers,  command=command,  configuration=self.configuration)

	def __parse_command_with_sequence_of_commands_single(self,  cli : str) -> tuple:
		unknown_arguments = list()
		commands = list()
		self._cli_parser.exit_on_error = False
		while cli:
			# Create a "local" namespace to avoid implicit inheritence of optional option values between commands.
			# This principle works because the values of the global optional arguments are not stored into the namespace but inside the AutoLaTeX configuration.
			args, cli1 =  self._cli_parser.parse_known_args(cli)
			if cli1:
				unknown_arguments.extend(cli1)
			if  args and hasattr(args,  '__command_callback_func'):
				func = getattr(args,  '__command_callback_func')
				if func:
					tpl = (func,  args)
					commands.append(tpl)
			if cli1 == cli:
				# Nothing was consumed
				return (commands,  unknown_arguments)
			cli = cli1
		return (commands,  unknown_arguments)

	def _parse_command_with_sequence_of_commands(self) -> str:
		'''
		Parse the command line in order to detect the optional arguments and the sequence of command arguments
		:return: the tuple with as first element the CLI commands, and the second element the list of unknown arguments.
		:rtype: tuple (commands, list)
		'''
		if self.__initial_argv is None or not isinstance(self.__initial_argv, list):
			cli = sys.argv[1:]
		else:
			cli = list(self.__initial_argv)
		(commands,  unknown_arguments) = self.__parse_command_with_sequence_of_commands_single(cli)
		# Check if a command is provided; and add the default command.
		if not commands:
			default_action = self.configuration.defaultCliAction
			if default_action:
				cli.insert(0,  default_action)
				(commands,  unknown_arguments) = self.__parse_command_with_sequence_of_commands_single(cli)
		return (commands,  unknown_arguments)

	def _create_default_command_arg_namespace(self) -> argparse.Namespace:
		'''
		Create the namespace that corresponds to a default command.
		:return: the namespace
		:rtype: Namespace
		'''
		namespace = argparse.Namespace()
		# add any action defaults that aren't present
		for action in self._cli_parser._actions:
			if action.dest is not SUPPRESS and not hasattr(namespace, action.dest) and action.default is not SUPPRESS:
				setattr(namespace, action.dest, action.default)
		# add any parser defaults that aren't present
		for dest in self._cli_parser._defaults:
			if not hasattr(namespace, dest):
				setattr(namespace, dest, self._defaults[dest])
		return namespace

	def _exitOnFailure(self):
		'''
		Exit the main program on failure.
		'''
		self.__exiter.exitOnFailure()

	def _exitOnSuccess(self):
		'''
		Exit the main program on success.
		'''
		self.__exiter.exitOnSuccess()

	def _exitOnException(self,  exception):
		'''
		Exit the main program on exception.
		:param exception: The exception.
		:type exception: exception
		'''
		self.__exiter.exitOException(exception)

	def _execute_commands(self,  args : list,  all_commands : dict):
		'''
		Execute the commands.
		:param args: List of arguments on the command line.
		:type args: list of argparse objects
		:param all_commands: Dict of all the available commands.
		:type all_commands: dict
		'''
		# Check existing command
		if not args:
			logging.error(_T('Unable to determine the command to run'))
			self.exitOnFailure()
			return

		# Run the sequence of commands
		for cmd, cmd_args in args:
			try:
				continuation = cmd(cmd_args)
				if not continuation:
					self._exitOnSuccess()
					return
			except BaseException as excp:
				logging.error(_T('Error when running the command: %s') % (str(excp)))
				self.__exiter.exitOnException(excp)
				return


	def _build_help_epilog(self) -> str:
		'''
		Build a string that could serve as help epilog.
		:return: the epilog text.
		:rtype: str
		'''
		return None

	def _init_logging_system(self):
		'''
		Configure the logging system.
		'''
		logging.basicConfig(format = self.configuration.logging.message,  level = self.configuration.logging.level)		

	def _detect_autolatex_configuration_file(self,  directory : str) -> str:
		'''
		Search for an AutoLaTeX configuration file in the given directory or one of its parent directories.
		:param directory: The start of the search.
		:type directory: str
		:return: the path to the configuration file, or None.
		:rtype: str
		'''
		if directory:
			root = os.path.abspath(os.sep)
			if os.path.isdir(directory):
				path = os.path.abspath(directory)
			else:
				path = os.path.dirname(os.path.abspath(directory))
			while (path and path != root and os.path.isdir(path)):
				filename = self.configuration.makeDocumentConfigFilename(path)
				if filename and os.path.isfile(filename):
					return filename
				path = os.path.dirname(path)
		return None

	def _create_cli_parser(self,  name : str,  version : str,  default_arg = None,  description : str= None,  osname : str = None,  platformname : str = None,  epilog=None):
		'''
		Create the instance of the CLI parser.
		:param name: The name of the program.
		:type name: str
		:param version: The version of the program.
		:type version: str
		:param default_arg: The default argument for the program.
		:type default_arg: str
		:param description: The description of the program.
		:type description: str
		:param osname: The name of the operating system.
		:type osname: str
		:param platformname: The name of the platform.
		:type platformname: str
		:param epilog: The epilog of the documentation.
		:type epilog: str
		:return: the created instance.
		'''
		if not description:
			description = _T('AutoLaTeX is a tool for managing small to large sized LaTeX documents. The user can easily perform all required steps to do such tasks as: preview the document, or produce a PDF file. AutoLaTeX will keep track of files that have changed and how to run the various programs that are needed to produce the output. One of the best feature of AutoLaTeX is to provide translator rules (aka. translators) to automatically generate the figures which will be included into the PDF.')
		if not osname:
			osname = os.name
		if not platformname:
			platformname = platform.system()
		parser = argparse.ArgumentParser(prog=name,  argument_default=default_arg,  description=description,  epilog=epilog, formatter_class=argparse.RawTextHelpFormatter)
		parser.version = _T("%s %s - %s/%s platform") % (name,  version,  osname,  platformname)
		return parser

	@property
	def cli_parser(self):
		'''
		Replies the CLI parser.
		:rtype: argparse object.
		'''
		return self._cli_parser
		
	def _add_standard_cli_options_general(self):
		'''
		Add standard CLI options in the "general" category.
		'''
		# --version
		self._cli_parser.add_argument('--version',
			action='version',
			help=_T('Display the version of AutoLaTeX'))

	def _add_standard_cli_options_path(self):
		'''
		Add standard CLI options in the "path configuration" category.
		'''
		path_group = self._cli_parser.add_argument_group(_T('path optional arguments'))

		input_method_group = path_group.add_mutually_exclusive_group()

		# --directory
		class DirectoryAction(argparse.Action):
			def __call__(actionself, parser, namespace, value, option_string=None):
				if os.path.isdir(value):
					self.configuration.documentDirectory = value
					self.configuration.documentFilename = None
				else:
					logging.error(_T("Invalid directory: %s") % (value))
					self.__exiter.exitOnFailure()
					return
		input_method_group.add_argument('-d', '--directory',
			action=DirectoryAction, 
			help=_T('Specify a directory in which a LaTeX document to compile is located. You could specify this option for each directory in which you have a LaTeX document to treat'))

		# --file
		class FileAction(argparse.Action):
			def __call__(actionself, parser, namespace, value, option_string=None):
				if os.path.isfile(value):
					self.configuration.setDocumentDirectoryAndFilename(value)
				else:
					logging.error(_T("File not found: %s") % (value))
					self.__exiter.exitOnFailure()
					return
		input_method_group.add_argument('-f', '--file',
			action=FileAction, 
			metavar=('TEX_FILE'), 
			help=_T('Specify the main LaTeX file to compile. If this option is not specified, AutoLaTeX will search for a TeX file in the current directory'))

		# --search-project-from
		class SearchProjectFromAction(argparse.Action):
			def __call__(actionself, parser, namespace, value, option_string=None):
				if value:
					config_file = self._detect_autolatex_configuration_file(value)
				else:
					config_file = self._detect_autolatex_configuration_file(self.configuration.documentDirectory)
				if config_file:
					config_reader = OldStyleConfigReader()
					config_reader.readDocumentConfigSafely(config_file,  self.configuration)
					self.__read_document_configuration = False
		path_group.add_argument('--search-project-from',
			action=SearchProjectFromAction, 
			metavar=('FILE'), 
			help=_T('When this option is specified, AutoLaTeX is searching a project configuration file (usually \'.autolatex_project.cfg\' on Unix platforms) in the directory of the specified FILE or in one of its ancestors'))

	def _add_standard_cli_options_output(self):
		'''
		Add standard CLI options in the "output configuration" category.
		'''
		output_group = self._cli_parser.add_argument_group(_T('output optional arguments'))

		output_type_group = output_group.add_mutually_exclusive_group()

		# --pdf
		class PdfAction(argparse.Action):
			def __call__(actionself, parser, namespace, value, option_string=None):
				self.configuration.pdfMode = True
		output_type_group.add_argument('--pdf',
			action=PdfAction, 
			nargs=0, 
			help=_T('Do the compilation to produce a PDF document'))

		# --dvi
		# --ps
		class DvipsAction(argparse.Action):
			def __call__(actionself, parser, namespace, value, option_string=None):
				self.configuration.pdfMode = False
		output_type_group.add_argument('--dvi',  '--ps',
			action=DvipsAction,
			nargs=0, 
			help=_T('Do the compilation to produce a DVI, XDV or Postscript document'))

		# --stdout
		# --stderr
		class StdouterrAction(argparse.Action):
			def __call__(actionself, parser, namespace, value, option_string=None):
				eprintpkg.is_standard_output = actionself.const

		std_output_group = output_group.add_mutually_exclusive_group()

		std_output_group.add_argument('--stdout',
			action=StdouterrAction, 
			const = True, 
			nargs=0, 
			help=_T('All the standard messages (no log message) are printed out on the standard output (stdout) of the process'))

		std_output_group.add_argument('--stderr',
			action=StdouterrAction, 
			const = False, 
			nargs=0, 
			help=_T('All the standard messages (no log message) are printed out on the standard error output (stderr) of the process'))

	def _add_standard_cli_options_tex(self):
		'''
		Add standard CLI options in the "tex configuration" category.
		'''
		tex_group = self._cli_parser.add_argument_group(_T('TeX optional arguments'))

		tex_tool_group = tex_group.add_mutually_exclusive_group()

		# --pdflatex
		class PdflatexCmdAction(argparse.Action):
			def __call__(actionself, parser, namespace, value, option_string=None):
				self.configuration.latexCompiler = 'pdflatex'
		tex_tool_group.add_argument('--pdflatex',
			action=PdflatexCmdAction,
			nargs=0, 
			help=_T('Use the LaTeX command: \'pdflatex\''))

		# --latex
		class LatexCmdAction(argparse.Action):
			def __call__(actionself, parser, namespace, value, option_string=None):
				self.configuration.latexCompiler = 'latex'
		tex_tool_group.add_argument('--latex',
			action=LatexCmdAction,
			nargs=0, 
			help=_T('Use the historical LaTeX command: \'latex\''))

		# --lualatex
		class LualatexCmdAction(argparse.Action):
			def __call__(actionself, parser, namespace, value, option_string=None):
				self.configuration.latexCompiler = 'lualatex'
		tex_tool_group.add_argument('--lualatex',
			action=LualatexCmdAction,
			nargs=0, 
			help=_T('Use the LaTeX command: \'lualatex\''))

		# --xelatex
		class XelatexCmdAction(argparse.Action):
			def __call__(actionself, parser, namespace, value, option_string=None):
				self.configuration.latexCompiler = 'xelatex'
		tex_tool_group.add_argument('--xelatex',
			action=XelatexCmdAction,
			nargs=0, 
			help=_T('Use the LaTeX command: \'xelatex\''))

		# --synctex
		# --nosynctex
		synctex_group = tex_group.add_mutually_exclusive_group()

		class SynctexAction(argparse.Action):
			def __call__(actionself, parser, namespace, value, option_string=None):
				self.configuration.generation.synctex = actionself.const

		synctex_group.add_argument('--synctex',
			action=SynctexAction,
			const = True, 
			nargs=0, 
			help=_T('Enable the generation of the output file with SyncTeX'))

		synctex_group.add_argument('--nosynctex',
			action=SynctexAction,
			const = False, 
			nargs=0, 
			help=_T('Disable the generation of the output file with SyncTeX'))

	def _add_standard_cli_options_translator(self):
		'''
		Add standard CLI options in the "translator configuration" category.
		'''
		translator_group = self._cli_parser.add_argument_group(_T('translator optional arguments'))

		# --auto
		# --noauto
		class AutoAction(argparse.Action):
			def __call__(actionself, parser, namespace, value, option_string=None):
				self.configuration.translators.is_translator_enable = actionself.const

		enable_translator_group = translator_group.add_mutually_exclusive_group()

		enable_translator_group.add_argument('--auto',
			action=AutoAction,
			const=True, 
			nargs=0, 
			help=_T('Enable the auto generation of the figures'))

		enable_translator_group.add_argument('--noauto',
			action=AutoAction,
			const=False, 
			nargs=0, 
			help=_T('Disable the auto generation of the figures'))

		# --exclude
		class ExcludeAction(argparse.Action):
			def __call__(actionself, parser, namespace, value, option_string=None):
				self.configuration.translators.setIncluded(value,  TranslatorLevel.DOCUMENT,  False)
		translator_group.add_argument('-e', '--exclude',
			action=ExcludeAction,
			metavar = ('TRANSLATOR'), 
			help=_T('Avoid AutoLaTeX to load the translator named TRANSLATOR'))

		# --include
		class IncludeAction(argparse.Action):
			def __call__(actionself, parser, namespace, value, option_string=None):
				self.configuration.translators.addIncludePath(value,  TranslatorLevel.DOCUMENT,  True)
		translator_group.add_argument('-i', '--include',
			action=IncludeAction,
			metavar = ('TRANSLATOR'), 
			help=_T('Force AutoLaTeX to load the translator named TRANSLATOR'))

		# --include-path
		class IncludePathAction(argparse.Action):
			def __call__(actionself, parser, namespace, value, option_string=None):
				paths = genutils.to_path_list(value,  self.configuration.documentDirectory)
				for path in paths:
					self.configuration.translators.addIncludePath(path)
		translator_group.add_argument('-I', '--include-path',
			action=IncludePathAction,
			metavar=('PATH'), 
			help=_T('Notify AutoLaTeX that it could find translator scripts inside the specified directories. The specified PATH could be a list of paths separated by the operating system\'s path separator (\':\' for Unix, \';\' for Windows for example)'))

		# --imgdirectory
		class ImgDirectoryAction(argparse.Action):
			def __call__(actionself, parser, namespace, value, option_string=None):
				paths = genutils.to_path_list(value,  self.configuration.documentDirectory)
				for path in paths:
					self.configuration.translators.addImagePath(path)
		translator_group.add_argument('-D', '--imgdirectory',
			action=ImgDirectoryAction,
			metavar=('DIRECTORY'), 
			help=_T('Specify a directory inside which AutoLaTeX will find the pictures which must be processed by the translators. Each time this option is put on the command line, a directory is added inside the list of the directories to explore'))

	def _add_standard_cli_options_biblio(self):
		'''
		Add standard CLI options in the "bibliography configuration" category.
		'''
		biblio_group = self._cli_parser.add_argument_group(_T('bibliography optional arguments'))

		# --biblio
		# --nobiblio
		class BiblioAction(argparse.Action):
			def __call__(actionself, parser, namespace, value, option_string=None):
				self.configuration.generation.is_biblio_enable = actionself.const

		enable_biblio_group = biblio_group.add_mutually_exclusive_group()

		enable_biblio_group.add_argument('--biblio',
			action=BiblioAction,
			const = True, 
			nargs = 0, 
			help=_T('Enable the call to the bibliography tool (BibTeX, Biber...)'))

		enable_biblio_group.add_argument('--nobiblio',
			action=BiblioAction,
			const = False, 
			nargs = 0, 
			help=_T('Disable the call to the bibliography tool (BibTeX, Biber...)'))

	def _add_standard_cli_options_index(self):
		'''
		Add standard CLI options in the "index configuration" category.
		'''
		index_group = self._cli_parser.add_argument_group(_T('index optional arguments'))

		# --defaultist
		class DefaultistAction(argparse.Action):
			def __call__(actionself, parser, namespace, value, option_string=None):
				self.configuration.generation.makeindexStyleFilename = self.configuration.get_system_ist_file()
		index_group.add_argument('--defaultist',
			action=DefaultistAction,
			nargs=0, 
			help=_T('Allow AutoLaTeX to use MakeIndex with the default style (\'.ist\' file)'))

		# --index
		index_e_group = index_group.add_mutually_exclusive_group()

		class IndexAction(argparse.Action):
			def __call__(actionself, parser, namespace, value, option_string=None):
				self.configuration.generation.is_index_enable = True
				if value:
					path = genutils.abspath(value,  self.configuration.documentDirectory)
					if os.path.isfile(path):
						self.configuration.generation.makeindexStyleFilename = path
					else:
						logging.error(_T("File not found: %s") % (value))
						self.__exiter.exitOnFailure()
						return
		index_e_group.add_argument('--index',
			action = IndexAction, 
			default = None, 
			nargs = '?', 
			metavar=('FILE'), 
			help=_T('Allow AutoLaTeX to use MakeIndex. If this option was specified with a value, the FILE value will be assumed to be an \'.ist\' file to pass to MakeIndex'))

		# --noindex
		class NoindexAction(argparse.Action):
			def __call__(actionself, parser, namespace, value, option_string=None):
				self.configuration.generation.is_index_enable = False
		index_e_group.add_argument('--noindex',
			action = NoindexAction,
			nargs = 0, 
			help=_T('Avoid AutoLaTeX to use MakeIndex'))

	def _add_standard_cli_options_glossary(self):
		'''
		Add standard CLI options in the "glossary configuration" category.
		'''
		glossary_group = self._cli_parser.add_argument_group(_T('glossary optional arguments'))

		# --glossary
		# --noglossary
		# --gloss
		# --nogloss
		class GlossaryAction(argparse.Action):
			def __call__(actionself, parser, namespace, value, option_string=None):
				self.configuration.generation.is_glossary_enable = actionself.const

		glossary_e_group = glossary_group.add_mutually_exclusive_group()

		glossary_e_group.add_argument('--glossary', '--gloss', 
			action=GlossaryAction,
			const = True, 
			nargs = 0, 
			help=_T('Enable the call to the glossary tool (makeglossaries...)'))

		glossary_e_group.add_argument('--noglossary', '--nogloss', 
			action=GlossaryAction,
			const = False, 
			nargs = 0, 
			help=_T('Disable the call to the glossary tool (makeglossaries...)'))


	def _add_standard_cli_options_warning(self):
		'''
		Add standard CLI options in the "warning configuration" category.
		'''
		warning_cfg_group = self._cli_parser.add_argument_group(_T('warning optional arguments'))

		# --file-line-warning
		# --nofile-line-warning
		class FilelinewarningAction(argparse.Action):
			def __call__(actionself, parser, namespace, value, option_string=None):
				self.configuration.generation.extendedWarnings = actionself.const

		warning_group = warning_cfg_group.add_mutually_exclusive_group()

		warning_group.add_argument('--file-line-warning',
			action=FilelinewarningAction,
			const = True, 
			nargs=0, 
			help=_T('Enable the extended format for warnings. This format add the filename and the line number where the warning is occuring, before the warning message by itself'))

		warning_group.add_argument('--nofile-line-warning',
			action=FilelinewarningAction,
			const = False, 
			nargs=0, 
			help=_T('Disable the extended format for warnings. This format add the filename and the line number where the warning is occuring, before the warning message by itself'))

	def _add_standard_cli_options_logging(self):
		'''
		Add standard CLI options in the "logging configuration" category.
		'''
		logging_group = self._cli_parser.add_argument_group(_T('logging optional arguments'))

		# --debug
		class DebugAction(argparse.Action):
			def __call__(actionself, parser, namespace, value, option_string=None):
				logger = logging.getLogger()
				logger.setLevel(logging.DEBUG)
				for handler in logger.handlers:
					handler.setLevel(logging.DEBUG)
		logging_group.add_argument('--debug',
			action=DebugAction,
			nargs=0, 
			help=_T('Run AutoLaTeX in debug mode, i.e., the maximum logging level'))

		# --quiet
		class QuietAction(argparse.Action):
			def __call__(actionself, parser, namespace, value, option_string=None):
				logger = logging.getLogger()
				logger.setLevel(logging.ERROR)
				for handler in logger.handlers:
					handler.setLevel(logging.ERROR)
		logging_group.add_argument('-q', '--quiet',
			action=QuietAction,
			nargs=0, 
			help=_T('Run AutoLaTeX without logging except the errors'))

		# --silent
		class SilentAction(argparse.Action):
			def __call__(actionself, parser, namespace, value, option_string=None):
				logger = logging.getLogger()
				logger.setLevel(LogLevel.OFF)
				for handler in logger.handlers:
					handler.setLevel(LogLevel.OFF)
		logging_group.add_argument('--silent',
			action=SilentAction,
			nargs=0, 
			help=_T('Run AutoLaTeX without logging, including no error message'))

		# --verbose
		class VerboseAction(argparse.Action):
			def __call__(actionself, parser, namespace, value, option_string=None):
				logger = logging.getLogger()
				level = logger.getEffectiveLevel()
				level = LogLevel.to_lower_level(level)
				if level < LogLevel.TRACE:
					# Specific behavior that shows up the configuration
					self.show_configuration()
					self.__exiter.exitOnSuccess()
				else:
					logger.setLevel(level)
					for handler in logger.handlers:
						handler.setLevel(level)
		logging_group.add_argument('-v', '--verbose',
			action=VerboseAction,
			nargs=0, 
			help=_T('Each time this option was specified, AutoLaTeX is more verbose'))

		# --Wall
		class WallAction(argparse.Action):
			def __call__(actionself, parser, namespace, value, option_string=None):
				logger = logging.getLogger()
				logger.setLevel(logging.FINE_WARNING)
				for handler in logger.handlers:
					handler.setLevel(logging.FINE_WARNING)
		logging_group.add_argument('--Wall',
			action=WallAction,
			nargs=0, 
			help=_T('Show all the warnings'))

		#--Wnone
		class WnoneAction(argparse.Action):
			def __call__(actionself, parser, namespace, value, option_string=None):
				logger = logging.getLogger()
				logger.setLevel(logging.ERROR)
				for handler in logger.handlers:
					handler.setLevel(logging.ERROR)
		logging_group.add_argument('--Wnone',
			action=WnoneAction,
			nargs=0, 
			help=_T('Show no warning'))

	def show_configuration(self):
		'''
		Show up the configuration of AutoLaTeX.
		'''
		eprintpkg.epprint(self.configuration)

	def add_standard_cli_options(self):
		'''
		Add the definition of the standard CLI options.
		'''
		self._add_standard_cli_options_general()
		self._add_standard_cli_options_path()
		self._add_standard_cli_options_output()
		self._add_standard_cli_options_tex()
		self._add_standard_cli_options_translator()
		self._add_standard_cli_options_biblio()
		self._add_standard_cli_options_index()
		self._add_standard_cli_options_glossary()
		self._add_standard_cli_options_warning()
		self._add_standard_cli_options_logging()

	def add_cli_options(self,  parser : object):
		'''
		Add the definition of the application CLI options.
		:param parser: the CLI parser
		'''
		pass

	def add_cli_positional_arguments(self,  parser : object):
		'''
		Add the definition of the application CLI positional arguments.
		:param parser: the CLI parser
		'''
		pass

	def _pre_run_program(self) -> tuple:
		'''
		Run the behavior of the main program before the specific behavior.
		:return: the tuple with as first element the CLI actions, and the second element the list of unknown arguments.
		:rtype: tuple (args, list)
		'''
		self.add_standard_cli_options()
		self.add_cli_options(self._cli_parser)
		self.add_cli_positional_arguments(self._cli_parser)

		if not self.configuration.documentDirectory:
			self.configuration.documentDirectory = os.getcwd()

		(cmds,  unknown_args) = self._parse_command_with_sequence_of_commands()
		
		if self.__read_document_configuration:
			config_file = self._detect_autolatex_configuration_file(self.configuration.documentDirectory)
			if config_file:
				config_reader = OldStyleConfigReader()
				config_reader.readDocumentConfigSafely(config_file,  self.configuration)

		return (cmds,  unknown_args)

	@abstractmethod
	def _run_program(self,  args : object,  unknown_args: list):
		'''
		Run the specific behavior.
		:param args: the CLI arguments that are not consumed by the argparse library.
		:type args: object
		:param unknown_args: the list of the unsupported arguments.
		:type unknown_args: list
		'''
		raise(Exception("You must implements the _run_program function into the subtype"))

	def _post_run_program(self,  args : object,  unknown_args: list):
		'''
		Run the behavior of the main program after the specific behavior.
		:param args: the CLI arguments that are not consumed by the argparse library.
		:type args: object
		:param unknown_args: the list of the unsupported arguments.
		:type unknown_args: list
		'''
		self.__exiter.exitOnSuccess()

	def run(self):
		'''
		Run the program.
		'''
		args,  unknown_arguments = self._pre_run_program()
		self._run_program(args,  unknown_arguments)
		self._post_run_program(args,  unknown_arguments)

