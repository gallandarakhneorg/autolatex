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

'''
AutoLaTeX Maker.
'''

import os
import re
import sys
import textwrap
import logging
import inspect
import json

from enum import IntEnum, unique
from dataclasses import dataclass
from sortedcontainers import SortedSet

from autolatex2.config.configobj import Config
from autolatex2.translator.translatorrepository import TranslatorRepository
from autolatex2.translator.translatorrunner import TranslatorRunner
import autolatex2.utils.utilfunctions as genutils
import autolatex2.tex.utils as texutils
import autolatex2.utils.extlogging as extlogging
from autolatex2.utils.runner import *
from autolatex2.tex.bibtex import BibTeXErrorParser
from autolatex2.tex.biber import BiberErrorParser
from autolatex2.tex.dependencyanalyzer import DependencyAnalyzer
from autolatex2.tex.citationanalyzer import AuxiliaryCitationAnalyzer
from autolatex2.tex.citationanalyzer import BiblatexCitationAnalyzer
from autolatex2.tex.indexanalyzer import IndexAnalyzer
from autolatex2.tex.utils import TeXWarnings

import gettext
_T = gettext.gettext

######################################################################
##
@unique
class TeXTools(IntEnum):
	'''
	Type of TeX tools supported by AutoLaTeX.
	'''
	bibtex = 0
	biber = 1
	makeindex = 2
	makeglossaries = 3
	dvips = 4
	pdflatex = 5
	latex = 6
	xelatex = 7
	lualatex = 8

######################################################################
##
@unique
class TeXCompiler(IntEnum):
	'''
	Type of TeX compilers supported by AutoLaTeX.
	'''
	pdflatex = TeXTools.pdflatex
	latex = TeXTools.latex
	xelatex = TeXTools.xelatex
	lualatex = TeXTools.lualatex

######################################################################
##
@unique
class BibCompiler(IntEnum):
	'''
	Type of bibliography compilers supported by AutoLaTeX.
	'''
	bibtex = TeXTools.bibtex
	biber = TeXTools.biber

######################################################################
##
@unique
class IndexCompiler(IntEnum):
	'''
	Type of index compilers supported by AutoLaTeX.
	'''
	makeindex = TeXTools.makeindex

######################################################################
##
@unique
class GlossaryCompiler(IntEnum):
	'''
	Type of glossary compilers supported by AutoLaTeX.
	'''
	makeglossaries = TeXTools.makeglossaries

######################################################################
##
@unique
class FileType(IntEnum):
	'''
	Type of a file in the AutoLaTeX making process.
	'''
	tex = 0
	pdf = 1

######################################################################
##
class FileDescription(object):
	'''
	Description of a file in the making process.
	'''

	def __init__(self, output_filename : str, fileType : FileType, input_filename : str,  mainfilename : str):
		'''
		Construct a file description.
		:param output_filename: Name of the file to generate.
		:type output_filename: str
		:param fileType: Type of the file. See FileType.
		:type fileType: FileType
		:param input_filename: Name of the file to read for generating this file.
		:type input_filename: str
		:param mainfilename: Name of the main file.
		:type mainfilename: str
		'''
		self.__type = fileType
		self.__output_filename = output_filename
		self.__input_filename = input_filename
		self.__mainfile = mainfilename
		self.__dependencies = SortedSet()
		self.__change = genutils.getFileLastChange(self.__output_filename)
		self.__use_biber = False

	def __str__(self):
		return self.__output_filename

	def __repr__(self):
		return self.__output_filename

	@property
	def fileType(self) -> FileType:
		'''
		Replies the type of the file.
		:rtype: FileType
		'''
		return self.__type

	@property
	def output_filename(self) -> str:
		'''
		Replies the name of the output file.
		:rtype: str
		'''
		return self.__output_filename

	@property
	def input_filename(self) -> str:
		'''
		Replies the name of the input file.
		:rtype: str
		'''
		return self.__input_filename

	@property
	def dependencies(self) -> dict:
		'''
		Replies the names of the files that are needed to build the current file.
		:rtype: dict
		'''
		return self.__dependencies

	@property
	def mainfilename(self) -> str:
		'''
		Replies the name of the main file.
		:rtype: str
		'''
		return self.__mainfile

	@property
	def change(self) -> bool:
		'''
		Replies the date of the last change of the file.
		:rtype: int
		'''
		return self.__change

	@property
	def use_biber(self) -> bool:
		'''
		Replies if Biber should be used to generate this file.
		:rtype: bool
		'''
		return self.__use_biber

	@use_biber.setter
	def use_biber(self,  use : bool):
		'''
		Change the flag that indicates if Biber should be used to generate this file.
		:param use: The flag.
		:type use: bool
		'''
		self.__use_biber = use


######################################################################
##
@dataclass
class DependencyEntry(object):
	file : FileDescription
	go_up : bool
	rebuild : bool
	parent : str
	
	def __init__(self,  file : FileDescription,  parent):
		'''
		Constructor.
		:param file: The description of the file.
		:type file: FileDescription
		:param parent: The name of the parent's file.
		:type parent: DependencyEntry
		'''
		self.file = file
		self.go_up = False
		self.rebuild = False
		self.parent = parent

	def __str__(self) -> str:
		return str(self.file)

	def __repr__(self) -> str:
		return repr(self.file)

######################################################################
##
class AutoLaTeXMaker(Runner):
	'''
	The maker for AutoLaTeX.
	'''

	__EXTENDED_WARNING_CODE = textwrap.dedent("""\
		%*************************************************************
		% CODE ADDED BY AUTOLATEX TO CHANGE THE OUPUT OF THE WARNINGS
		%*************************************************************
		\\makeatletter
		\\newcount\\autolatex@@@lineno
		\\newcount\\autolatex@@@lineno@delta
		\\xdef\\autolatex@@@mainfile@real{::::REALFILENAME::::}
		\\def\\autolatex@@@mainfile{autolatex_autogenerated.tex}
		\\xdef\\autolatex@@@filename@stack{{\\autolatex@@@mainfile}{\\autolatex@@@mainfile}}
		\\global\\let\\autolatex@@@currentfile\\autolatex@@@mainfile
		\\def\\autolatex@@@filename@stack@push#1{%
			\\xdef\\autolatex@@@filename@stack{{#1}\\autolatex@@@filename@stack}%
		}
		\\def\\autolatex@@@filename@stack@pop@split#1#2\\@nil{%
			\\gdef\\autolatex@@@currentfile{#1}%
			\\gdef\\autolatex@@@filename@stack{#2}%
		}
		\\def\\autolatex@@@filename@stack@pop{%
			\\expandafter\\autolatex@@@filename@stack@pop@split\\autolatex@@@filename@stack\\@nil}
		\\def\\autolatex@@@update@filename{%
			\\ifx\\autolatex@@@mainfile\\autolatex@@@currentfile%
				\\edef\\autolatex@@@warning@filename{\\autolatex@@@mainfile@real}%
				\\global\\autolatex@@@lineno@delta=::::AUTOLATEXHEADERSIZE::::\\relax%
			\\else%
				\\edef\\autolatex@@@warning@filename{\\autolatex@@@currentfile}%
				\\global\\autolatex@@@lineno@delta=0\\relax%
			\\fi%
			{\\filename@parse{\\autolatex@@@warning@filename}\\global\\let\\autolatex@@@filename@ext\\filename@ext}%
			\\xdef\\autolatex@@@generic@warning@beginmessage{!!!![BeginWarning]\\autolatex@@@warning@filename:\\ifx\\autolatex@@@filename@ext\\relax.tex\\fi:}%
			\\xdef\\autolatex@@@generic@warning@endmessage{!!!![EndWarning]\\autolatex@@@warning@filename}%
		}
		\\def\\autolatex@@@openfile#1{%
			\\expandafter\\autolatex@@@filename@stack@push{\\autolatex@@@currentfile}%
			\\xdef\\autolatex@@@currentfile{#1}%
			\\autolatex@@@update@filename%
		}
		\\def\\autolatex@@@closefile{%
			\\autolatex@@@filename@stack@pop%
			\\autolatex@@@update@filename%
		}
		\\let\\autolatex@@@InputIfFileExists\\InputIfFileExists
		\\long\\def\\InputIfFileExists#1#2#3{%
			\\autolatex@@@openfile{#1}%
			\\autolatex@@@InputIfFileExists{#1}{#2}{#3}%
			\\autolatex@@@closefile%
		}
		\\let\\autolatex@@@input\\@input
		\\long\\def\\@input#1{%
			\\autolatex@@@openfile{#1}%
			\\autolatex@@@input{#1}%
			\\autolatex@@@closefile%
		}
		\\global\\DeclareRobustCommand{\\GenericWarning}[2]{%
			\\global\\autolatex@@@lineno\\inputlineno\\relax%
			\\global\\advance\\autolatex@@@lineno\\autolatex@@@lineno@delta\\relax%
			\\begingroup
			\\def\\MessageBreak{^^J#1}%
			\\set@display@protect
			\\immediate\\write\\@unused{^^J\\autolatex@@@generic@warning@beginmessage\\the\\autolatex@@@lineno: #2\\on@line.^^J\\autolatex@@@generic@warning@endmessage^^J}%
			\\endgroup
		}
		\\autolatex@@@update@filename
		\\makeatother
		%*************************************************************
		""")

	__COMMAND_DEFINITIONS = {
		TeXTools.pdflatex.value: {
			'cmd': 'pdflatex',
			'flags': ['-halt-on-error', '-interaction', 'batchmode', '-file-line-error'],
			'to_dvi': ['-output-format=dvi'],
			'to_ps': None,
			'to_pdf': ['-output-format=pdf'],
			'synctex': '-synctex=1',
			'jobname': '-jobname',
			'output_dir':  '-output-directory', 
			'ewarnings': __EXTENDED_WARNING_CODE,
		},
		TeXTools.latex.value: {
			'cmd': 'latex',
			'flags': ['-halt-on-error', '-interaction', 'batchmode', '-file-line-error'],
			'to_dvi': ['-output-format=dvi'],
			'to_ps': None,
			'to_pdf': ['-output-format=pdf'],
			'synctex': '-synctex=1',
			'jobname': '-jobname',
			'output_dir':  '-output-directory', 
			'ewarnings': __EXTENDED_WARNING_CODE,
		},
		TeXTools.xelatex.value: {
			'cmd': 'xelatex',
			'flags': ['-halt-on-error', '-interaction', 'batchmode', '-file-line-error'],
			'to_dvi': ['-no-pdf'],
			'to_ps': None,
			'to_pdf': [],
			'synctex': '-synctex=1',
			'jobname': '-jobname',
			'output_dir':  '-output-directory', 
			'ewarnings': __EXTENDED_WARNING_CODE,
		},
		TeXTools.lualatex.value: {
			'cmd': 'luatex',
			'flags': ['-halt-on-error', '-interaction', 'batchmode', '-file-line-error'],
			'to_dvi': ['-output-format=dvi'],
			'to_ps': None,
			'to_pdf': ['-output-format=pdf'],
			'synctex': '-synctex=1',
			'jobname': '-jobname',
			'output_dir':  '-output-directory', 
			'ewarnings': __EXTENDED_WARNING_CODE,

		},
		TeXTools.bibtex.value: {
			'cmd': 'bibtex',
			'flags': [],
		},
		TeXTools.biber.value: {
			'cmd': 'biber',
			'flags': [],
		},
		TeXTools.makeindex.value: {
			'cmd': 'makeindex',
			'flags': [],
			'index_style_flag': '-s',
		},
		TeXTools.makeglossaries.value: {
			'cmd': 'makeglossaries',
			'flags': [],
			'glossary_style_flag': '-s',
		},
		TeXTools.dvips.value: {
			'cmd': 'dvips',
			'flags': [],
			'output':'-o', 
		},
	}

	@staticmethod
	def __callback_function_selector(x):
		if inspect.ismethod(x):
			if (x.__name__.startswith('__build_callback_')):
				return True
		return False

	def __init__(self, translatorRunner : TranslatorRunner):
		'''
		Construct the make of translators.
		:param translatorRunner: The runner of translators.
		:type translatorRunner: TranslatorRunner
		'''
		self.translatorRunner = translatorRunner
		self.configuration = translatorRunner.configuration
		# Initialization of the compiler definitions and the command-line options are differed to the "__internal_register_commands" method factory
		self.__instance_compiler_definition = None
		# Initialization of the callback definitions and the command-line options are differed to the "__internal_register_callbacks" method factory
		self.__callback_functions = None
		# Initialize fields by resetting them
		self.reset()

	@staticmethod
	def create(configuration : Config) :
		'''
		Static factory method for creating an instance of AutoLaTeXMaket with the "standard" building method.
		:param configuration: the configuration to use.
		:param configuration: Config
		:return: the instance of the maker
		:rtype: AutoaTeXMaker
		'''
		# Create the translator repository
		repository = TranslatorRepository(configuration)
		# Create the runner of translators
		runner = TranslatorRunner(repository)
		# Create the general maker
		maker = AutoLaTeXMaker(runner)
		# Set the maker from the configuration
		ddir = configuration.documentDirectory
		dfile = configuration.documentFilename
		if ddir:
			fn = os.path.join(ddir,  dfile)
		else:
			fn = dfile
		maker.addRootFile(fn)
		return maker

	def __internal_register_callbacks(self) -> dict:
		'''
		Register the different callbacks according to the current configuration. This method should not be called from outside the class.
		It is based on the method factory design pattern.
		:return: The callback functions.
		:rtype: dict
		'''
		if self.__callback_functions is None:
			self.__callback_functions = dict(inspect.getmembers(self, predicate=AutoLaTeXMaker.__callback_function_selector))
		return self.__callback_functions

	def reset_commands(self):
		'''
		Reset the external tool commands and rebuild them from the current configuration.
		'''
		self.__instance_compiler_definition = None

	def __internal_register_commands(self):
		'''
		Build the different commands according to the current configuration. This method should not be called from outside the class.
		It is based on the method factory design pattern.
		'''
		if self.__instance_compiler_definition is None:
			compiler = self.configuration.generation.latexCompiler
			if compiler is None:
				compilerNum = TeXTools.pdflatex.value if self.configuration.generation.pdfMode else TeXTools.latex.value
				compiler = AutoLaTeXMaker.__COMMAND_DEFINITIONS[compilerNum]['cmd']
			else:
				compilerNum = TeXCompiler[compiler].value

			self.__instance_compiler_definition = AutoLaTeXMaker.__COMMAND_DEFINITIONS[compilerNum].copy()
			if not self.__instance_compiler_definition:
				raise Exception[_T("Cannot find a definition of the command line for the LaTeX compiler '%s'") % (compiler)]

			outtype = 'pdf' if self.configuration.generation.pdfMode else 'ps'

			# LaTeX
			self.__latexCLI = list()
			if self.configuration.generation.latexCLI:
				self.__latexCLI.extend(self.configuration.generation.latexCLI)
			else:
				self.__latexCLI.append(self.__instance_compiler_definition['cmd'])
				self.__latexCLI.extend(self.__instance_compiler_definition['flags'])
				if ('to_%s' % (outtype)) not in self.__instance_compiler_definition:
					raise Exception(_T("No command definition for '%s/%s'") % (compiler, outtype))
				# Support of SyncTeX
				if self.configuration.generation.synctex and self.__instance_compiler_definition['synctex']:
					if isinstance(self.__instance_compiler_definition['synctex'], list):
						self.__latexCLI.extend(self.__instance_compiler_definition['synctex'])
					else:
						self.__latexCLI.append(self.__instance_compiler_definition['synctex'])

				target = self.__instance_compiler_definition['to_%s' % (outtype)]
				if target:
					if isinstance(target, list):
						self.__latexCLI.extend(target)
					else:
						self.__latexCLI.append(target)
				elif outtype == 'ps':
					if isinstance(self.__instance_compiler_definition['to_dvi'], list):
						self.__latexCLI.extend(self.__instance_compiler_definition['to_dvi'])
					else:
						self.__latexCLI.append(self.__instance_compiler_definition['to_dvi'])
				else:
					raise Exception(_T('Invalid maker state: cannot find the command line to compile TeX files.'))

			if self.configuration.generation.latexFlags:
				self.__latexCLI.extend(self.configuration.generation.latexFlags)

			# BibTeX
			self.__bibtexCLI = list()
			if self.configuration.generation.bibtexCLI:
				self.__bibtexCLI.extend(self.configuration.generation.bibtexCLI)
			else:
				cmd = AutoLaTeXMaker.__COMMAND_DEFINITIONS[BibCompiler.bibtex.value]
				if not cmd:
					raise Exception(_T("No command definition for 'bibtex'"))
				self.__bibtexCLI.append(cmd['cmd'])
				self.__bibtexCLI.extend(cmd['flags'])

			if self.configuration.generation.bibtexFlags:
				self.__bibtexCLI.extend(self.configuration.generation.bibtexFlags)

			# Biber
			self.__biberCLI = list()
			if self.configuration.generation.biberCLI:
				self.__biberCLI.extend(self.configuration.generation.biberCLI)
			else:
				cmd = AutoLaTeXMaker.__COMMAND_DEFINITIONS[BibCompiler.biber.value]
				if not cmd:
					raise Exception(_T("No command definition for 'biber'"))
				self.__biberCLI.append(cmd['cmd'])
				self.__biberCLI.extend(cmd['flags'])

			if self.configuration.generation.biberFlags:
				self.__biberCLI.extend(self.configuration.generation.biberFlags)

			# MakeIndex
			self.__makeindexCLI = list()
			if self.configuration.generation.makeindexCLI:
				self.__makeindexCLI.extend(self.configuration.generation.makeindexCLI)
			else:
				cmd = AutoLaTeXMaker.__COMMAND_DEFINITIONS[IndexCompiler.makeindex.value]
				if not cmd:
					raise Exception(_T("No command definition for 'makeindex'"))
				self.__makeindexCLI.append(cmd['cmd'])
				self.__makeindexCLI.extend(cmd['flags'])

			if self.configuration.generation.makeindexFlags:
				self.__makeindexCLI.extend(self.configuration.generation.makeindexFlags)

			# MakeGlossaries
			self.__makeglossariesCLI = list()
			if self.configuration.generation.makeglossaryCLI:
				self.__makeglossariesCLI.extend(self.configuration.generation.makeglossaryCLI)
			else:
				cmd = AutoLaTeXMaker.__COMMAND_DEFINITIONS[GlossaryCompiler.makeglossaries.value]
				if not cmd:
					raise Exception(_T("No command definition for 'makeglossaries'"))
				self.__makeglossariesCLI.append(cmd['cmd'])
				self.__makeglossariesCLI.extend(cmd['flags'])

			if self.configuration.generation.makeglossaryFlags:
				self.__makeglossariesCLI.extend(self.configuration.generation.makeglossaryFlags)

			# Dvips
			self.__dvipsCLI = list()
			if self.configuration.generation.dvipsCLI:
				self.__dvipsCLI.extend(self.configuration.generation.dvipsCLI)
			else:
				cmd = AutoLaTeXMaker.__COMMAND_DEFINITIONS[TeXTools.dvips.value]
				if not cmd:
					raise Exception(_T("No command definition for 'dvips'"))
				self.__dvipsCLI.append(cmd['cmd'])
				self.__dvipsCLI.extend(cmd['flags'])

			if self.configuration.generation.dvipsFlags:
				self.__dvipsCLI.extend(self.configuration.generation.dvipsFlags)

			# Support of extended warnings
			if self.configuration.generation.extendedWarnings and 'ewarnings' in self.__instance_compiler_definition and self.__instance_compiler_definition['ewarnings']:
				code = self.__instance_compiler_definition['ewarnings'].strip()
				s = str(-(code.count('\n') + 1))
				code = code.replace('::::AUTOLATEXHEADERSIZE::::', s)
				self.__latexWarningCode = code
				self.__isExtendedWarningEnable = True
			else:
				self.__latexWarningCode = ''
				self.__isExtendedWarningEnable = False

	def reset(self):
		'''
		Reset the maker.
		'''
		self.__rootFiles = set()
		self.__reset_warnings()
		self.__reset_process_data()

	def __reset_process_data(self):
		self.__files = dict()
		self.__stamps = dict()

	def __reset_warnings(self):
		'''
		Reset the lists of warnings.
		'''
		self.__standardsWarnings = set()
		self.__detailledWarnings = list()

	@property
	def compilerDefinition(self) -> dict:
		'''
		The definition of the LaTeX compiler that must be used by this maker.
		:rtype: dict
		'''
		self.__internal_register_commands()
		return self.__instance_compiler_definition

	@property
	def extendedWarningsEnabled(self) -> bool:
		'''
		Replies if the extended warnings are supported by the TeX compiler.
		:rtype: bool
		'''
		self.__internal_register_commands()
		return self.__isExtendedWarningEnable

	@property
	def extendedWarningsCode(self) -> str:
		'''
		Replies the TeX code that permits to output the extended warnings.
		:rtype: str
		'''
		self.__internal_register_commands()
		return self.__latexWarningCode

	@property
	def latexCLI(self) -> list:
		'''
		The command-line that is used for running the LaTeX tool.
		:rtype: list
		'''
		self.__internal_register_commands()
		return self.__latexCLI

	@property
	def bibtexCLI(self) -> list:
		'''
		The command-line that is used for running the BibTeX tool.
		:rtype: list
		'''
		self.__internal_register_commands()
		return self.__bibtexCLI

	@property
	def biberCLI(self) -> list:
		'''
		The command-line that is used for running the Biber tool.
		:rtype: list
		'''
		self.__internal_register_commands()
		return self.__biberCLI

	@property
	def makeindexCLI(self) -> list:
		'''
		The command-line that is used for running the makeindex tool.
		:rtype: list
		'''
		self.__internal_register_commands()
		return self.__makeindexCLI

	@property
	def makeglossariesCLI(self) -> list:
		'''
		The command-line that is used for running the makeglossaries tool.
		:rtype: list
		'''
		self.__internal_register_commands()
		return self.__makeglossariesCLI

	@property
	def dvipsCLI(self) -> list:
		'''
		The command-line that is used for running the dvips tool.
		:rtype: list
		'''
		self.__internal_register_commands()
		return self.__dvipsCLI

	@property
	def rootFiles(self) -> set:
		'''
		The root files that are involved within the lastest compilation process.
		:rtype: set
		'''
		return self.__rootFiles

	def addRootFile(self,  filename : str):
		'''
		Add root file.
		:param filename: The name of the root file.
		:type filename: str
		'''
		self.__rootFiles.add(filename)

	@property
	def files(self) -> dict:
		'''
		The files that are involved within the lastest compilation process.
		:rtype: dict
		'''
		return self.__files

	@property
	def standardWarnings(self) -> set:
		'''
		The standard LaTeX warnings that are discovered during the lastest compilation process.
		:rtype: set
		'''
		return self.__standardsWarnings

	@property
	def extendedWarnings(self) -> list:
		'''
		The extended warnings that are discovered during the lastest compilation process.
		:rtype: set
		'''
		return self.__detailledWarnings

	def __extract_info_from_tex_log_file(self, logFile : str, loop : bool) -> bool:
		'''
		Parse the TeX log in order to extract warnings and replies if another TeX compilation is needed.
		:param logFile: The filename of the log file that is used for detecting the compilation loop.
		:type logFile: str
		:param loop: Indicate if the compilation loop is enable.
		:type loop: bool
		:rtype: bool
		'''
		warning = False
		currentLogBlock = ''
		if os.path.exists(logFile):
			with open(logFile, 'r') as f:
				lastline = ''
				line = f.readline()
				while line:
					lastline += line
					# Detect standatd TeX warnings
					if re.search('\\.\\s*$', lastline):
						if texutils.extractTeXWarningFromLine(lastline, self.__standardsWarnings):
							if loop:
								return True
					# Parse and output the detailled warning messages
					if self.__isExtendedWarningEnable:
						if warning:
							if line.startswith('!!!![EndWarning]'):
								m = re.search('^(.*?):([^:]*):([0-9]+):\\s*(.*?)\\s*$', currentLogBlock)
								if m:
									wdetails = dict()
									wdetails['filename'] = m.group(1)
									wdetails['extension'] = m.group(2)
									wdetails['lineno'] = int(m.group(3))
									wdetails['message'] = m.group(4)
									self.__detailledWarnings.append(wdetails)
								warning = False
								currentLogBlock = ''
							else:
								l = line
								if not re.search('\.\n+$', l):
									l = re.sub('\s+$', '',  l)
								currentLogBlock += l
						else:
							m = re.search('^'+re.escape('!!!![BeginWarning]')+'(.*)$', line)
							if m:
								l = m.group(1)
								if not re.search('\.\n+$', l):
									l = re.sub('\s+$', '',  l)
								currentLogBlock += l
								warning = True
					line = f.readline()
				if re.search('\\.\\s*$', lastline) and texutils.extractTeXWarningFromLine(lastline, self.__standardsWarnings):
					if loop:
						return True
		# Output the detailled wanring message that was not already output
		if warning and currentLogBlock:
			m = re.search('^(.*?):([^:]*):([0-9]+):\\s*(.*?)\\s*$', currentLogBlock)
			if m:
				wdetails = dict()
				wdetails['filename'] = m.group(1)
				wdetails['extension'] = m.group(2)
				wdetails['lineno'] = int(m.group(3))
				wdetails['message'] = m.group(4)
				self.__detailledWarnings.append(wdetails)
		return False

	def run_latex(self, filename : str, loop : bool = False) -> int:
		'''
		Launch the LaTeX tool and return the number of times the
		tool was launched.
		:param filename: The name TeX file to compile.
		:type filename: str
		:param loop: Indicates if this function may loop on the LaTeX compilation when it is requested by the LaTeX tool. Default value: False.
		:type loop: bool
		:return: The number of runs
		:rtype: int
		'''
		self.__internal_register_commands()
		if filename in self.__files:
			mfn = self.__files[filename].mainfilename
			if mfn is not None and mfn != '':
				filename = mfn
		logFile = genutils.basename2(filename, texutils.getTeXFileExtensions()) + '.log'
		continueToCompile = True
		nbRuns = 0
		while continueToCompile:
			logging.debug(_T('LATEX: %s') % (os.path.basename(filename)))
			self.__reset_warnings()
			if os.path.isfile(logFile):
				os.remove(logFile)
			exitcode = 0
			if self.__isExtendedWarningEnable:
				with open(filename, "r") as f:
					content = f.readlines()
				autofile = genutils.basename2(filename, texutils.getTeXFileExtensions()) + "_autolatex_autogenerated.tex"
				with open(autofile, "w") as f:
					code = self.__latexWarningCode.replace('::::REALFILENAME::::', filename)
					f.write(code)
					f.write("\n")
					f.write(''.join(content))
					f.write("\n")
				try:
					cmd = self.__latexCLI.copy()
					if 'jobname' in self.__instance_compiler_definition and self.__instance_compiler_definition['jobname'] != '':
						cmd.append(self.__instance_compiler_definition['jobname'])
						cmd.append(genutils.basename(filename, texutils.getTeXFileExtensions()))
					if 'output_dir' in self.__instance_compiler_definition and self.__instance_compiler_definition['output_dir'] is not None and self.__instance_compiler_definition['output_dir'] != '':
						cmd.append(self.__instance_compiler_definition['output_dir'])
						cmd.append(os.path.dirname(filename))
					else:
						logging.warning(_T('LATEX: no command-line option provided for changing the output directory'))
					cmd.append(autofile)
					cmd = Runner.normalizeCommand(cmd)
					nbRuns += 1
					(sout, serr, sex, exitcode) = Runner.runCommand(*cmd)
				finally:
					genutils.unlink(autofile)
			else:
				cmd = self.__latexCLI.copy()
				cmd.append(os.path.relpath(filename))
				cmd = Runner.normalizeCommand(cmd)
				nbRuns += 1
				(sout, serr, sex, exitcode) = Runner.runCommand(*cmd)

			if exitcode != 0:
				logging.debug(_T("LATEX: Error when processing %s") % (os.path.basename(filename)))

				# Parse the log to extract the blocks of messages
				(fatalError, logBlocks) = texutils.parseTeXLogFile(logFile)

				# Display the message
				if fatalError:

					# Test if the message is an emergency stop
					if re.search('^.*?:[0-9]+:\\s*emergency\\s+stop\\.', fatalError, re.I | re.M):
						for block in logBlocks:
							m = re.search('^\\s*!\\s*(.*?)\\s*$', block, re.S | re.M)
							if m:
								fatalError += "\n" + m.group(1)

					fatalError = re.sub('^latex_autogenerated.tex:',  os.path.basename(filename) + ':',  fatalError)
					logging.debug(_T("LATEX: The first error found in the log file is:"))
					extlogging.multiline_error(fatalError)
					logging.debug(_T("LATEX: End of error log."))
				else:
					logging.error(_T("LATEX: Unable to extract the error from the log. Please read the log file."))

				sys.exit(255)

			else:
				continueToCompile = self.__extract_info_from_tex_log_file(logFile, loop)

		return nbRuns

	def run_bibtex(self, filename : str) -> dict:
		'''
		Launch the BibTeX tool (bibtex, biber, etc) once time and replies a dictionary that describes any error.
		The returned dictionnary has the keys: filename, lineno and message.
		:param filename: The name TeX file to compile.
		:type filename: str
		:rtype: dict
		'''
		self.__internal_register_commands()
		if filename in self.__files:
			mfn = self.__files[filename].mainfilename
			if mfn is not None and mfn != '':
				filename = mfn
		self.__reset_warnings()
		auxFile = genutils.basename2(filename,  texutils.getTeXFileExtensions()) 
		if self.configuration.generation.is_biber:
			logging.debug(_T('BIBER: %s') % (os.path.basename(auxFile)))
			cmd = self.__biberCLI.copy()
		else:
			auxFile += '.aux'
			logging.debug(_T('BIBTEX: %s') % (os.path.basename(auxFile)))
			cmd = self.__bibtexCLI.copy()
		cmd.append(os.path.relpath(auxFile))
		cmd = Runner.normalizeCommand(cmd)
		if self.configuration.generation.is_biber:
			logging.trace(_T('BIBER: Command line is: %s') % (' '.join(cmd)))
		else:
			logging.trace(_T('BIBTEX: Command line is: %s') % (' '.join(cmd)))
		(sout, serr, sex, exitcode) = Runner.runCommand(*cmd)
		if exitcode != 0:
			if self.configuration.generation.is_biber:
				logging.debug(_T('BIBER: error when processing %s') % (os.path.basename(auxFile)))
			else:
				logging.debug(_T('BIBTEX: error when processing %s') % (os.path.basename(auxFile)))
			log = sout
			if not log:
				log = serr
			if log:
				if self.configuration.generation.is_biber:
					logParser = BiberErrorParser()
				else:
					logParser = BibTeXErrorParser()
				currentError = logParser.parseLog(auxFile,  log)
				if currentError:
					return currentError
			currentError = {'filename': auxFile,  'lineno': 0,  'message': sout + "\n" + serr}
			return currentError
		return None

	def run_makeindex(self, filename : str) -> bool:
		'''
		Launch the MakeIndex tool once time.
		The success status if the run of MakeIndex is replied.
		:param filename: The filename of the index file to compile.
		:type filename: str
		:return: True to continue the process. False to stop.
		:rtype: bool
		'''
		self.__internal_register_commands()
		idxExt = texutils.getIndexFileExtensions()[0]
		idxFile = genutils.basename2(filename,  texutils.getIndexFileExtensions()) + idxExt
		logging.debug(_T('MAKEINDEX: %s') % (os.path.basename(idxFile)))
		self.__reset_warnings()
		cmd = self.__makeindexCLI.copy()
		istFile = self.configuration.generation.makeindexStyleFilename
		if istFile:
			cmd_def = AutoLaTeXMaker.__COMMAND_DEFINITIONS[IndexCompiler.makeindex.value]
			if not cmd_def:
				raise Exception(_T("No command definition for 'makeindex'"))
			cmd.append(cmd_def['index_style_flag'])
			cmd.append(os.path.relpath(istFile))
		cmd.append(os.path.relpath(idxFile))
		cmd = Runner.normalizeCommand(cmd)
		(sout, serr, sex, exitcode) = Runner.runCommand(*cmd)
		return exitcode == 0

	def run_makeglossaries(self, filename : str) -> bool:
		'''
		Launch the MakeGlossaries tool once time.
		The success status if the run of MakeGlossaries is replied.
		:param filename: The filename of the tex file to compile.
		:type filename: str
		:return: True to continue the process. False to stop.
		:rtype: bool
		'''
		self.__internal_register_commands()
		texWoExt = genutils.basename2(filename,  texutils.getTeXFileExtensions())
		glsFile = texWoExt + texutils.getGlossaryFileExtensions()[0]
		logging.debug(_T('MAKEGLOSSARIES: %s') % (os.path.basename(glsFile)))
		self.__reset_warnings()
		cmd = self.__makeglossariesCLI.copy()
		istFile = self.configuration.generation.makeindexStyleFilename
		if istFile:
			cmd_def = AutoLaTeXMaker.__COMMAND_DEFINITIONS[GlossaryCompiler.makeglossaries.value]
			if not cmd_def:
				raise Exception(_T("No command definition for 'makeglossaries'"))
			cmd.append(cmd_def['glossary_style_flag'])
			cmd.append(os.path.relpath(istFile))
		cmd.append(os.path.relpath(texWoExt))
		cmd = Runner.normalizeCommand(cmd)
		(sout, serr, sex, exitcode) = Runner.runCommand(*cmd)
		return exitcode == 0

	def __create_file_description(self,  output_filename : str,  type : str,  input_filename : str,  mainfilename : str) -> FileDescription:
		'''
		Create an entry into the list of files involved into the execution process.
		:param output_filename: The name of the output file.
		:type output_filename: str
		:param type: The type of the file.
		:type type: str
		:param input_filename: The name of the input file.
		:type input_filename: str
		:param mainfilename: The name of the main file associated to this file in the process.
		:type mainfilename: str
		'''
		if output_filename not in self.__files:
			desc = FileDescription(output_filename, type, input_filename, mainfilename)
			self.__files[output_filename] = desc
			return True
		return False

	def __compute_tex_dependencies(self,  root_filename : str,  root_dir : str) -> bool:
		'''
		Build the dependency tree for the given TeX file. Replies if the dependencies have been changed.
		:param root_filename: The root TeX filename.
		:type root_filename: str
		:param root_dir: The name of the root directory.
		:type root_dir: str
		:return: True if the dependency tree has changed.
		:rtype: bool
		'''
		files = list([root_filename])
		changed = False
		while files:
			file = files[0]
			files = files[1:]
			if os.path.isfile(file):
				chg = self.__create_file_description(file,  'tex',  file,  None if file == root_filename else root_filename)
				changed = changed or chg
				file_description = self.__files[file]
				analyzer = DependencyAnalyzer(file,  root_dir)
				analyzer.run()
				# Treat the pure TeX files
				for type in analyzer.getDependencyTypes():
					deps = analyzer.getDependencies(type)
					for dep in deps:
						chg = self.__create_file_description(dep,  type,  root_filename,  None if type != 'tex' or dep == root_filename else root_filename)
						file_description.dependencies.add(dep)
						changed = True
						if type == 'tex':
							files.append(dep)
				# Treat the bibliography files that  are referred from the TeX code
				biblio_deps = analyzer.getDependencies('biblio')
				if biblio_deps:
					for bibdb,  bibdt in biblio_deps.items():
						bblfiles = set()
						if 'bib' in bibdt and bibdt['bib']:
							for bibfile in bibdt['bib']:
								bblfile = genutils.basename2(bibfile,  ['.bib']) + '.bbl'
								self.__create_file_description(bblfile,  'bbl',  root_filename,  root_filename)
								file_description.dependencies.add(bblfile)
								self.__files[bblfile].dependencies.add(bibfile)
								changed = True
								self.__files[bblfile].use_biber = analyzer.is_biber
								bblfiles.add(bblfile)
						for bibext in ['bst', 'bbc',  'cbx']:
							if bibext in bibdt and bibdt[bibext]:
								for bibdepfile in bibdt[bibext]:
									chg = self.__create_file_description(bibdepfile,  bibext,  file, root_filename)
									changed = changed or chg
									for bblfile in bblfiles:
										self.__files[bblfile].dependencies.add(bibdepfile)
										changed = True
				# Treat the index files that  are referred from the TeX code
				if analyzer.is_makeindex:
					idxfile = genutils.basename2(root_filename,  texutils.getTeXFileExtensions()) + '.idx'
					self.__create_file_description(idxfile,  'idx',  root_filename, root_filename)
					indfile = genutils.basename2(idxfile,  ['.idx']) + '.ind'
					self.__create_file_description(indfile,  'ind', idxfile, root_filename)
					self.__files[indfile].dependencies.add(idxfile)
					self.__files[root_filename].dependencies.add(indfile)
					changed = True
				# Treat the glossaries files that  are referred from the TeX code
				if analyzer.is_glossary:
					glofile = genutils.basename2(root_filename,  texutils.getTeXFileExtensions()) + '.glo'
					self.__create_file_description( glofile,  'glo', root_filename,  root_filename)
					glsfile = genutils.basename2(glofile,  ['.glo']) + '.gls'
					self.__create_file_description(glsfile,  'gls', root_filename,  root_filename)
					self.__files[glsfile].dependencies.add(glofile)
					self.__files[root_filename].dependencies.add(glsfile)
					changed = True
		return changed

	def __compute_aux_dependencies(self,  root_filename : str,  root_dir : str) -> bool:
		'''
		Build the dependency tree for the given Aux file. Replies if the dependencies have been changed.
		The references in the auxiliary file is related to specific bibliography systems, e.g., multibib.
		:param root_filename: The Aux root filename.
		:type root_filename: str
		:param root_dir: The name of the root directory.
		:type root_dir: str
		:rtype: bool
		'''
		texrootfilename = genutils.basename2(root_filename,  '.aux') + '.tex'
		onlyfiles = [os.path.join(root_dir,  f) for f in os.listdir(root_dir) if f.lower().endswith('.aux') and os.path.isfile(os.path.join(root_dir, f))]
		changed = False
		for file in onlyfiles:
			analyzer = AuxiliaryCitationAnalyzer(file)
			analyzer.run()
			styles = analyzer.styles
			databases = analyzer.databases
			if styles:
				for style in styles:
					bstfile = os.path.abspath(style + '.bst')
					if os.path.isfile(bstfile):
						chg = self.__create_file_description(bstfile,  'bst', texrootfilename, texrootfilename)
						changed = changed or chg
						for db in databases:
							bblfile = os.path.abspath(genutils.basename2(db,  '.bib') + '.bbl')
							self.__create_file_description(bblfile,  'bbl', texrootfilename, texrootfilename)
							changed = changed or chg
							self.__files[bblfile].dependencies.add(bstfile)
							self.__files[filename].dependencies.add(bblfile)
							changed = True
			if databases:
				for db in databases:
					bibfile = os.path.abspath(db)
					if os.path.isfile(bibfile):
						self.__create_file_description(bibfile,  'bib', texrootfilename,  texrootfilename)
						bblfile = genutils.basename2(bibfile,  '.bib') + '.bbl'
						self.__create_file_description(bblfile,  'bbl', texrootfilename,  texrootfilename)
						self.__files[bblfile].dependencies.add(bibfile)
						self.__files[filename].dependencies.add(bblfile)
						changed = True
		return changed

	def compute_dependencies(self,  filename : str,  readAuxFile : bool = True) -> dict:
		'''
		Build the dependency tree for the given TeX file.
		:param filename: The TeX filename.
		:type filename: str
		:param readAuxFile: Indicates if the auxilliary files must be read too. Default is True.
		:type readAuxFile: bool
		:return: The tuple with the root dependency file and the dictionary of dependencies.
		:rtype: tuple(str, dict)
		'''
		root_dir = os.path.dirname(filename)
		# Add dependency for the final PDF file
		pdfFile = genutils.basename2(filename,  texutils.getTeXFileExtensions()) + '.pdf'
		self.__create_file_description(pdfFile,  'pdf', filename,  filename)
		self.__files[pdfFile].dependencies.add(filename)
		# TeX files
		self.__compute_tex_dependencies(filename,  root_dir)
		# Aux files
		if readAuxFile:
			self.__compute_aux_dependencies(filename,  root_dir)
		return (pdfFile,  self.__files)

	def __need_rebuild(self,  rootchange : int,  filename : str,  parent : DependencyEntry,  description : FileDescription) -> bool:
		'''
		Test if a rebuild is needed for the given files.
		:param rootchange: Time stamp of the root file.
		:type rootchange: int
		:param filename: Name of the file to test.
		:type filename: str
		:param parent: Parent element.
		:type parent: DependencyEntry
		:param parent: Description of the file to test.
		:type parent: FileDescription
		:rtype: bool
		'''
		if description.change is None or not os.path.isfile(filename):
			return True
		exts = os.path.splitext(filename)
		ext = exts[-1]
		if ext:
			if ext == '.bbl':
				if description.use_biber:
					# Parse the BCF file to detect the citations
					bcfFile = genutils.basename2(filename, '.bbl') + '.bcf'
					bcfAnalyzer = BiblatexCitationAnalyzer(bcfFile)
					currentMd5 = bcfAnalyzer.md5() or ''
					oldMd5 = self.__stamps['bib'][bcfFile] or ''
					if currentMd5 != oldMd5:
						self.__stamps['bib'][bcfFile] = currentMd5
						return True
				else:
					pass
					# Parse the AUX file to detect the citations
					auxFile = genutils.basename2(filename, '.bbl') + '.aux'
					auxAnalyzer = AuxiliaryCitationAnalyzer(auxFile)
					currentMd5 = auxAnalyzer.md5() or ''
					oldMd5 = self.__stamps['bib'][auxFile] or ''
					if currentMd5 != oldMd5:
						self.__stamps['bib'][auxFile] = currentMd5
						return True
				return False
			elif  ext  == '.ind':
				# Parse the IDX file to detect the index definitions
				idxFile = genutils.basename2(filename, '.ind') + '.idx'
				idxAnalyzer = IndexAnalyzer(idxFile)
				currentMd5 = idxAnalyzer.md5 or ''
				if not 'idx' in self.__stamps:
					self.__stamps = dict()
				if idxFile in self.__stamps['idx']:
					oldMd5 = self.__stamps['idx'][idxFile]
				else:
					oldMd5 = ''
				if  currentMd5 != oldMd5:
					self.__stamps['idx'][idxFile] = currentMd5
					return True
				return False
		return description.change is None or description.change > rootchange

	def __internal_build_callback_funcname(self,  fileType : str) -> str:
		'''
		Build the internal name of a building callback function.
		:param fileType: The type of file concerned by the callback.
		:type fileType: str
		:return: the name of the callback function.
		:rtype: str
		'''
		return '_' + self.__class__.__name__ + '__build_callback_' + str(fileType).lower()

	def build_internal_execution_list(self,  rootFile : str,  root_pdf_file : str,  dependencies : dict,  forceChanges : bool = False):
		'''
		Build the list of files that needs to be generated in the best order. For each file, a building function named "_build_<ext>" is defined and must be invoked.
		:param rootFile: The LaTeX file to compile.
		:type rootFile: str
		:param root_pdf_file: The root PDF file to generate.
		:type root_pdf_file: str
		:param dependencies: The tree of the dependencies for the root file.
		:type dependencies: dict
		:param forceChanges: Indicates all the files should be considered as changed. Default value is: False.
		:type forceChange: bool
		:return: the list of files to be built.
		:rtype: list
		'''
		builds = list()
		# Go through the dependency tree with en iterative algorithm
		rootchange = self.__files[root_pdf_file].change
		element = DependencyEntry(self.__files[root_pdf_file], None) 
		iterator = [ element ]
		while iterator:
			element = iterator.pop()
			current_filename = element.file.output_filename
			current_description = self.__files[current_filename]
			deps = current_description.dependencies
			if element.go_up or not deps:
				if forceChanges or element.rebuild or self.__need_rebuild(rootchange, current_filename, element.parent, current_description):
					if element.parent:
						element.parent.rebuild = True
					method_name = self.__internal_build_callback_funcname(current_description.fileType)
					if method_name in self.__internal_register_callbacks():
						builds.append(element.file)
			else:
				iterator.append(element)
				element.go_up = True
				for dep in deps:
					if dep in self.__files:
						dep_obj = self.__files[dep]
						if dep_obj:
							child = DependencyEntry(dep_obj, element)
							iterator.append(child)
		return builds

	def run_translators(self,  forceGeneration : bool = False):
		'''
		Run the image translators. Replies the list of images that is detected.
		The replied dict associates each source image (keys) to the generated image's filename (values) or None if no file was generated by the call to this function.
		:param forceGeneration: Indicates if the image generation is forced to be run on all the images (True) or if only the changed source images are considered for the image generation (False). Default is: False.
		:type forceGeneration: bool
		:rtype: dict
		'''
		self.translatorRunner.sync()
		images = self.translatorRunner.getSourceImages()
		generatedImages = dict()
		for img in images:
			generatedImage = self.translatorRunner.generateImage(infile = img, onlymorerecent = not forceGeneration)
			generatedImages[img] = generatedImage
		return generatedImages

	def read_build_stamps(self,  folder : str,  basename : str = ".autolatex_stamp"):
		'''
		Read the build stamps. There stamps are used to memorize the building dates of each element (latex, bibtex, etc.).
		Fill up the "__stamps" fields and reply them.
		:param folder: name of the folder in which the stamps file is located.
		:type folder: str
		:param basename: name of the temporary file. Default is: ".autolatex_stamp".
		:type basename: str
		:return: the "__stamps" field.
		:rtype: dict
		'''
		stampFile = os.path.join(folder,  basename)
		self.__stamps = dict()
		self.__stamps['bib'] = dict()
		self.__stamps['idx'] = dict()
		if os.access(stampFile, os.R_OK):
			with open(stampFile,  'r') as sf:
				line = sf.readline()
				while line:
					m = re.match('^BIB\\(([^)]+?)\\)\\:(.+)$',  line)
					if m:
						k = m.group(1)
						n = m.group(2)
						self.__stamps['bib'][n] = k
					else:
						m = re.match('^IDX\\(([^)]+?)\\)\\:(.+)$',  line)
						if m:
							k = m.group(1)
							n = m.group(2)
							self.__stamps['idx'][n] = k
					line = sf.readline()
		return self.__stamps

	def write_build_stamps(self,  folder : str,  basename : str = ".autolatex_stamp",  stamps : dict = None):
		'''
		Write the build stamps. There stamps are used to memorize the building dates of each element (latex, bibtex, etc.).
		:param folder: name of the folder in which the stamps file is located.
		:type folder: str
		:param basename: name of the temporary file. Default is: ".autolatex_stamp".
		:type basename: str
		:param stamps: Stamps to write
		:type stamps: dict
		'''
		stampFile = os.path.join(folder,  basename)
		if stamps is None:
			s = self.__stamps
		else:
			s = stamps
		with open(stampFile,  'w') as sf:
			if s:
				if 'bib' in s and s['bib']:
					for (k,  n) in s['bib'].items():
						sf.write("BIB(")
						sf.write(str(n))
						sf.write("):")
						sf.write(str(k))
						sf.write("\n")
				if 'idx' in s and s['idx']:
					for (k,  n) in s['idx'].items():
						sf.write("IDX(")
						sf.write(str(n))
						sf.write("):")
						sf.write(str(k))
						sf.write("\n")

	def __launch_file_build(self,  root_file : str,  root_pdf_file : str, input : FileDescription) -> bool:
		'''
		Launch the building process for generating the output file for the given input file.
		This function launch one of the callback building functions, named "__build_callback_<ext>" if it exists.
		This function is an utility function 
		:param root_file: Name of the root file (tex document).
		:type root_file: str
		:param root_pdf_file: Name of the root PDF file.
		:type root_pdf_file: str
		:param input: Description of the input file.
		:type input: FileDescription
		:return: The continuation statut, i.e. True if the build could continue.
		:rtype: bool
		'''
		if input:
			type = input.fileType
			if type:
				method_name = self.__internal_build_callback_funcname(type)
				if method_name:
					cb = self.__internal_register_callbacks()
					if method_name in cb:
						func = cb[method_name]
						continuation = func(root_file, input)
						if not continuation:
							return False
		return True

	def run_dvips(self, filename : str):
		'''
		Launch the tool for converting a DVI file to a Postscript file. Replies the description of the current error.
		:param filename: The name dvi file to convert.
		:type filename: str
		:rtype: tuple
		'''
		self.__internal_register_commands()
		logging.debug(_T('DVIPS: %s') % (os.path.basename(filename)))
		if filename in self.__files:
			mfn = self.__files[filename].mainfilename
			if mfn is not None and mfn != '':
				filename = mfn
		output = genutils.basename2(filename,  '.dvi') + '.ps'
		cmd_def = AutoLaTeXMaker.__COMMAND_DEFINITIONS[TeXTools.dvips.value]
		self.__reset_warnings()
		cmd = self.__dvipsCLI.copy()
		cmd.append(cmd_def['output'])
		cmd.append(os.path.relpath(output))
		cmd.append(os.path.relpath(filename))
		cmd = Runner.normalizeCommand(cmd)
		(sout, serr, sex, exitcode) = Runner.runCommand(*cmd)
		if exitcode != 0:
			logging.debug(_T('DVIPS: error when processing %s') % (os.path.basename(filename)))
			currentError = {'filename': filename,  'lineno': 0,  'message': sout + "\n" + serr}
			return currentError
		return None

	def to_json_dependencies(self,  root_file : str,  dependencies : dict) -> str:
		'''
		Convert the internal file dependencies to a Json format.
		:param root_file: The name of the file that is at the root of the dependencies.
		:type root_file: str
		:param dependencies: The dependencies tree.
		:type dependencies: dict
		:return: The Json description of the file dependencies.
		:rtype: str
		'''
		js = dict()
		js['file'] = root_file
		if root_file in dependencies and dependencies[root_file]:
			js['dependencies'] = list()
			self.__to_json_dependencies(dependencies,  dependencies[root_file].dependencies,  js['dependencies'])
		return json.dumps(js, indent=4)

	def __to_json_dependencies(self,  dependencies : dict,  direct_deps,  dep_list : dict):
		is_complex = False
		complex_list = list()
		simple_list = list()
		for dep in direct_deps:
			dep_desc = dict()
			dep_desc['file'] = dep
			complex_list.append(dep_desc)
			if dep in dependencies and dependencies[dep].dependencies:
				dep_desc['dependencies'] = list()
				is_complex = True
				self.__to_json_dependencies(dependencies,  dependencies[dep].dependencies, dep_desc['dependencies'])
			simple_list.append(dep)
		if is_complex:
			dep_list.extend(complex_list)
		else:
			dep_list.extend(simple_list)

	def build(self) -> bool:
		'''
		Launch the building process (image generation, latex, bibtex, makeindex, glossary)
		:return: True to continue process. False to stop the process.
		'''
		self.__reset_process_data()
		for rootFile in self.__rootFiles:
			rootDir = os.path.dirname(rootFile)

			# Read building stamps
			self.read_build_stamps(rootDir)

			# Launch one LaTeX compilation to be sure that every files that are expected are generated
			self.run_latex(rootFile, False);

			# Compute the dependencies of the file
			root_dep_file,  dependencies = self.compute_dependencies(rootFile)
			extlogging.multiline_debug(_T("Dependency Tree = %s") % (self.to_json_dependencies(root_dep_file,  dependencies)))

			# Construct the build list and launch the required builds
			builds = self.build_internal_execution_list(rootFile,  root_dep_file,  dependencies)
			if logging.getLogger().isEnabledFor(logging.DEBUG):
				if builds:
					logging.debug(_T("Build list:"))
					idx = 1
					for b in builds:
						logging.debug(_T("%d) %s") % (idx,  b.output_filename))
						idx = idx + 1
				else:
					logging.debug(_T("Empty build list"))

			# Build the files
			if builds:
				for file in builds:
					continuation = self.__launch_file_build(rootFile, root_dep_file,  file)
					if not continuation:
						return False

			# Output the warnings from the last TeX builds
			if self.extendedWarnings:
				for w in self.extendedWarnings:
					logging.warning(w)
				self.__reset_warnings()

			# Write building stamps
			self.write_build_stamps(rootDir)

			# Generate the Postscript file when requested
			if not self.configuration.generation.pdfMode:
				basename = genutils.basename2(rootFile, texutils.getTeXFileExtensions())
				dviFile = basename + '.dvi'
				dviDate = genutils.getFileLastChange(dviFile)
				if dviDate is not None:
					psFile = genutils.basename2(basename,  '.dvi') + '.ps'
					psDate = genutils.getFileLastChange(psFile)
					if psDate  is None or dviDate >= psDate:
						self.run_dvips(dviFile)

			# Compute the log filename
			main_tex_file = self.__files[rootFile].mainfilename or rootFile
			logFile = genutils.basename2(main_tex_file,  texutils.getTeXFileExtensions()) + '.log'

			# Detect warnings if not already done
			if not self.standardWarnings:
				self.__extract_info_from_tex_log_file(logFile, False)

			# Output the last LaTeX warning indicators.
			if logging.getLogger().isEnabledFor(logging.WARNING):
				if TeXWarnings.multiple_definition in self.standardWarnings:
					s = _T("LaTeX Warning: There were multiply-defined labels.")
					if self.extendedWarningsEnabled:
						sys.stderr.write("!!" + logFile + ":W1: " + s + "\n")
					else:
						logging.warning(s)
				if TeXWarnings.undefined_reference in self.standardWarnings:
					s = _T("LaTeX Warning: There were undefined references.")
					if self.extendedWarningsEnabled:
						sys.stderr.write("!!" + logFile + ":W2: " + s + "\n")
					else:
						logging.warning(s)
				if TeXWarnings.undefined_citation in self.standardWarnings:
					s = _T("LaTeX Warning: There were undefined citations.")
					if self.extendedWarningsEnabled:
						sys.stderr.write("!!" + logFile + ":W3: " + s + "\n")
					else:
						logging.warning(s)
				if TeXWarnings.other_warning in self.standardWarnings:
					logging.warning((_T("LaTeX Warning: Please look inside %s for the other the warning messages.") % (basename(logFile))) + "\n")
			return True

	def __build_callback_bbl(self,  root_file : str,  input : FileDescription) -> bool:
		'''
		Generate BBL (bibtex) file.
		:param root_file: Name of the root file (tex document).
		:type root_file: str
		:param input: Description of the input file.
		:type input: FileDescription
		:return: The continuation statut, i.e. True if the build could continue.
		:rtype: bool
		'''
		if self.configuration.generation.is_biblio_enable:
			error = self.run_bibtex(input.input_filename) 
			if error:
				extlogging.multiline_error(error['message'])
				return False
		return True

	def __build_callback_ind(self,  root_file : str,  input : FileDescription) -> bool:
		'''
		Generate IND (index) file.
		:param root_file: Name of the root file (tex document).
		:type root_file: str
		:param input: Description of the input file.
		:type input: FileDescription
		:return: The continuation statut, i.e. True if the build could continue.
		:rtype: bool
		'''
		if self.configuration.generation.is_index_enable:
			return self.run_makeindex(input.input_filename)
		return True

	def __build_callback_gls(self,  root_file : str,  input : FileDescription) -> bool:
		'''
		Generate GLS (glossary) file.
		:param root_file: Name of the root file (tex document).
		:type root_file: str
		:param input: Description of the input file.
		:type input: FileDescription
		:return: The continuation statut, i.e. True if the build could continue.
		:rtype: bool
		'''
		if self.configuration.generation.is_glossary_enable:
			return self.run_makeglossaries(input.input_filename)
		return True

	def __build_callback_pdf(self,  root_file : str,  input : FileDescription) -> bool:
		'''
		Generate root PDF file.
		:param root_file: Name of the root file (tex document).
		:type root_file: str
		:param input: Description of the input file.
		:type input: FileDescription
		:return: The continuation statut, i.e. True if the build could continue.
		:rtype: bool
		'''
		self.run_latex(input.input_filename, True)
		return True
