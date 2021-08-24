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
Configuration for the generation.
'''

import autolatex2.utils.utilfunctions as genutils

class GenerationConfig(object):
	'''
	Configuration of a AutoLaTeX instance.
	'''

	def __init__(self):
		self.__isPdfMode = True
		self.__extendedWarnings = True
		self.__makeindex = True
		self.__biblio = True
		self.__synctex = False
		self.__latexCompiler = None
		self.__latexCLI = list()
		self.__latexFlags = list()
		self.__bibtexCLI = list()
		self.__bibtexFlags = list()
		self.__biberCLI = list()
		self.__biberFlags = list()
		self.__makeindexCLI = list()
		self.__makeindexFlags = list()
		self.__makeindexStyleFilename = None
		self.__makeglossaryCLI = list()
		self.__makeglossaryFlags = list()
		self.__dvipsCLI = list()
		self.__dvipsFlags = list()
		self.__useBiber = False
		self.__useBiblatex = False
		self.__useMakeindex = False
		self.__useMultibib = False
		self.__enableBiblio = True
		self.__enableIndex = True
		self.__enableGlossary = True

	@property
	def pdfMode(self) -> bool:
		'''
		Replies if the generation is in PDF mode.
		:return: True if the generated file is PDF. False if it is Postscript.
		:rtype: bool
		'''
		return self.__isPdfMode

	@pdfMode.setter
	def pdfMode(self, mode : bool):
		'''
		Set if the generation is in PDF mode.
		:param mode: True if the generated file is PDF. False if it is Postscript.
		:type mode: bool
		'''
		self.__isPdfMode = bool(mode)

	@property
	def extendedWarnings(self) -> bool:
		'''
		Replies if the extended warning feature is enabled.
		:return: True if the extended warning feature is used.
		:rtype: bool
		'''
		return self.__extendedWarnings

	@extendedWarnings.setter
	def extendedWarnings(self, enable : bool):
		'''
		Replies if the extended warning feature is enabled.
		:param enable: True if the extended warning feature is used.
		:type enable: bool
		'''
		self.__extendedWarnings = bool(enable)

	@property
	def makeindex(self) -> bool:
		'''
		Replies if the 'makeindex' tools is enabled during the generation.
		:return: True if 'makeindex' should be invoked when necessary.
		:rtype: bool
		'''
		return self.__makeindex

	@makeindex.setter
	def makeindex(self, enable : bool):
		'''
		Set if the 'makeindex' tools is enabled during the generation.
		:param enable: True if 'makeindex' should be invoked when necessary.
		:type enable: bool
		'''
		self.__makeindex = bool(enable)

	@property
	def biblio(self) -> bool:
		'''
		Replies if the 'bibliography' tools is enabled during the generation.
		:return: True if 'bibliography' should be invoked when necessary.
		:rtype: bool
		'''
		return self.__biblio

	@biblio.setter
	def biblio(self, enable : bool):
		'''
		Set if the 'bibliography' tools is enabled during the generation.
		:param enable: True if 'bibliography' should be invoked when necessary.
		:type enable: bool
		'''
		self.__biblio = bool(enable)

	@property
	def synctex(self) -> bool:
		'''
		Replies if the synctex feature is enabled.
		:return: True if synctex enabled.
		:rtype: bool
		'''
		return self.__synctex

	@synctex.setter
	def synctex(self, enable : bool):
		'''
		Set if the synctex feature is enabled.
		:param enable: True if synctex enabled.
		:type enable: bool
		'''
		self.__synctex = bool(enable)

	@property
	def latexCompiler(self) -> str:
		'''
		Replies the name of the latex compiler to use. If None, the latex compiler will be determined later.
		:return: pdflatex, latex, xelatex, lualatex.
		:rtype: str
		'''
		return self.__latexCompiler

	@latexCompiler.setter
	def latexCompiler(self, name : str):
		'''
		Set the name of the latex compiler to use.
		:param name: Must be one of pdflatex, latex, xelatex, lualatex.  If None, the latex compiler will be determined later.
		:type name: str
		'''
		self.__latexCompiler = name

	@property
	def latexCLI(self) -> list:
		'''
		Replies the command-line for latex.
		:rtype: list
		'''
		return self.__latexCLI

	@latexCLI.setter
	def latexCLI(self, cli):
		'''
		Set the command-line for latex.
		:type cli: str or list
		'''
		if cli is None:
			self.__latexCLI = list()
		elif isinstance(cli, list):
			self.__latexCLI = cli
		else:
			self.__latexCLI = genutils.parseCLI(cli)

	@property
	def latexFlags(self) -> list:
		'''
		Replies additional flags for the latex compiler.
		:rtype: list
		'''
		return self.__latexFlags

	@latexFlags.setter
	def latexFlags(self, flags):
		'''
		Set additional flags for the latex compiler.
		:type flags: str or list
		'''
		if flags is None:
			self.__latexFlags = list()
		elif isinstance(flags, list):
			self.__latexFlags = flags
		else:
			self.__latexFlags = genutils.parseCLI(flags)

	@property
	def bibtexCLI(self) -> list:
		'''
		Replies the command-line for bibtex.
		:rtype: list
		'''
		return self.__bibtexCLI

	@bibtexCLI.setter
	def bibtexCLI(self, cli):
		'''
		Set the command-line for bibtex.
		:type cli: str or list
		'''
		if cli is None:
			self.__bibtexCLI = list()
		elif isinstance(cli, list):
			self.__bibtexCLI = cli
		else:
			self.__bibtexCLI = genutils.parseCLI(cli)

	@property
	def bibtexFlags(self) -> list:
		'''
		Replies additional flags for the bibtex compiler.
		:rtype: list
		'''
		return self.__bibtexFlags

	@bibtexFlags.setter
	def bibtexFlags(self, flags):
		'''
		Set additional flags for the bibtex compiler.
		:type flags: str or list
		'''
		if flags is None:
			self.__bibtexFlags = list()
		elif isinstance(flags, list):
			self.__bibtexFlags = flags
		else:
			self.__bibtexFlags = genutils.parseCLI(flags)

	@property
	def biberCLI(self) -> list:
		'''
		Replies the command-line for biber.
		:rtype: list
		'''
		return self.__biberCLI

	@biberCLI.setter
	def biberCLI(self, cli):
		'''
		Set the command-line for biber.
		:type cli: str or list
		'''
		if cli is None:
			self.__biberCLI = list()
		elif isinstance(cli, list):
			self.__biberCLI = cli
		else:
			self.__biberCLI = genutils.parseCLI(cli)

	@property
	def biberFlags(self) -> list:
		'''
		Replies additional flags for the biber compiler.
		:rtype: list
		'''
		return self.__biberFlags

	@biberFlags.setter
	def biberFlags(self, flags):
		'''
		Set additional flags for the biber compiler.
		:type flags: str or list
		'''
		if flags is None:
			self.__biberFlags = list()
		elif isinstance(flags, list):
			self.__biberFlags = flags
		else:
			self.__biberFlags = genutils.parseCLI(flags)

	@property
	def is_biber(self) -> bool:
		'''
		Replies if the Biber tool must be used instead of the standard bibtex.
		:rtype: bool
		'''
		return self.__useBiber

	@is_biber.setter
	def is_biber(self, enable : bool):
		'''
		Change the flag that indicates if the Biber tool must be used instead of the standard bibtex.
		:type enable: bool
		'''
		self.__useBiber = enable

	@property
	def is_biblatex(self) -> bool:
		'''
		Replies if the biblatex tool must be used.
		:rtype: bool
		'''
		return self.__useBiblatex

	@is_biblatex.setter
	def is_biblatex(self, enable : bool):
		'''
		Change the flag that indicates if the biblatex tool must be used.
		:type enable: bool
		'''
		self.__useBiblatex = enable
	
	@property
	def is_makeindex(self) -> bool:
		'''
		Replies if the makeindex tool must be used.
		:rtype: bool
		'''
		return self.__useMakeindex

	@is_makeindex.setter
	def is_makeindex(self, enable : bool):
		'''
		Change the flag that indicates if the makeindex tool must be used.
		:type enable: bool
		'''
		self.__useMakeindex = enable

	@property
	def is_multibib(self) -> bool:
		'''
		Replies if the multibib tool must be used.
		:rtype: bool
		'''
		return self.__useMultibib

	@is_multibib.setter
	def is_multibib(self, enable : bool):
		'''
		Change the flag that indicates if the multibib tool must be used.
		:type enable: bool
		'''
		self.__useMultibib = enable

	@property
	def is_biblio_enable(self) -> bool:
		'''
		Replies if the bibliography generation is activated.
		:rtype: bool
		'''
		return self.__enableBiblio

	@is_biblio_enable.setter
	def is_biblio_enable(self, enable : bool):
		'''
		Change the activation flag for the bibliography generation.
		:type enable: bool
		'''
		self.__enableBiblio = enable

	@property
	def is_index_enable(self) -> bool:
		'''
		Replies if the index generation is activated.
		:rtype: bool
		'''
		return self.__enableIndex

	@is_index_enable.setter
	def is_index_enable(self, enable : bool):
		'''
		Change the activation flag for the index generation.
		:type enable: bool
		'''
		self.__enableIndex = enable

	@property
	def is_glossary_enable(self) -> bool:
		'''
		Replies if the glossary generation is activated.
		:rtype: bool
		'''
		return self.__enableGlossary

	@is_glossary_enable.setter
	def is_glossary_enable(self, enable : bool):
		'''
		Change the activation flag for the glossary generation.
		:type enable: bool
		'''
		self.__enableGlossary = enable

	@property
	def makeglossaryCLI(self) -> list:
		'''
		Replies the command-line for makeglossary.
		:rtype: list
		'''
		return self.__makeglossaryCLI

	@makeglossaryCLI.setter
	def makeglossaryCLI(self, cli):
		'''
		Set the command-line for makeglossary.
		:type cli: str or list
		'''
		if cli is None:
			self.__makeglossaryCLI = list()
		elif isinstance(cli, list):
			self.__makeglossaryCLI = cli
		else:
			self.__makeglossaryCLI = genutils.parseCLI(cli)

	@property
	def makeglossaryFlags(self) -> list:
		'''
		Replies additional flags for the makeglossary compiler.
		:rtype: list
		'''
		return self.__makeglossaryFlags

	@makeglossaryFlags.setter
	def makeglossaryFlags(self, flags):
		'''
		Set additional flags for the makeglossary compiler.
		:type flags: str or list
		'''
		if flags is None or isinstance(flags, list):
			self.__makeglossaryFlags = flags
		else:
			self.__makeglossaryFlags = genutils.parseCLI(flags)

	@property
	def makeindexCLI(self) -> list:
		'''
		Replies the command-line for makeindex.
		:rtype: list
		'''
		return self.__makeindexCLI

	@makeindexCLI.setter
	def makeindexCLI(self, cli):
		'''
		Set the command-line for makeindex.
		:type cli: str or list
		'''
		if cli is None:
			self.__makeindexCLI = list()
		elif isinstance(cli, list):
			self.__makeindexCLI = cli
		else:
			self.__makeindexCLI = genutils.parseCLI(cli)

	@property
	def makeindexFlags(self) -> list:
		'''
		Replies additional flags for the makeindex compiler.
		:rtype: list
		'''
		return self.__makeindexFlags

	@makeindexFlags.setter
	def makeindexFlags(self, flags):
		'''
		Set additional flags for the makeindex compiler.
		:type flags: str or list
		'''
		if flags is None:
			self.__makeindexFlags = list()
		elif isinstance(flags, list):
			self.__makeindexFlags = flags
		else:
			self.__makeindexFlags = genutils.parseCLI(flags)

	@property
	def makeindexStyleFilename(self) -> str:
		'''
		Replies filename that is the MakeIndex style to be used.
		:rtype: str
		'''
		return self.__makeindexStyleFilename

	@makeindexStyleFilename.setter
	def makeindexStyleFilename(self, filename : str):
		'''
		Set the filename that is the MakeIndex style to be used.
		:type filename: str
		'''
		self.__makeindexStyleFilename = filename

	@property
	def dvipsCLI(self) -> list:
		'''
		Replies the command-line for dvi2ps.
		:rtype: list
		'''
		return self.__dvipsCLI

	@dvipsCLI.setter
	def dvipsCLI(self, cli):
		'''
		Set the command-line for dvips.
		:type cli: str or list
		'''
		if cli is None:
			self.__dvipsCLI = list()
		elif isinstance(cli, list):
			self.__dvipsCLI = cli
		else:
			self.__dvipsCLI = genutils.parseCLI(cli)

	@property
	def dvipsFlags(self) -> list:
		'''
		Replies additional flags for the dvips compiler.
		:rtype: list
		'''
		return self.__dvipsFlags

	@dvipsFlags.setter
	def dvipsFlags(self, flags):
		'''
		Set additional flags for the dvips compiler.
		:type flags: str or list
		'''
		if flags is None or isinstance(flags, list):
			self.__dvipsFlags = flags
		else:
			self.__dvipsFlags = genutils.parseCLI(flags)

