#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2013-15  Stephane Galland <galland@arakhne.org>
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

import re

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
		self.__latexCompiler = 'pdflatex'
		self.__latexCLI = None
		self.__latexFlags = None
		self.__bibtexCLI = None
		self.__bibtexFlags = None
		self.__biberCLI = None
		self.__biberFlags = None
		self.__makeindexCLI = None
		self.__makeindexFlags = None
		self.__dvipsCLI = None
		self.__dvipsFlags = None

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
		Replies the name of the latex compiler to use.
		:return: pdflatex, latex, xelatex, lualatex.
		:rtype: str
		'''
		return self.__latexCompiler

	@latexCompiler.setter
	def latexCompiler(self, name : str):
		'''
		Set the name of the latex compiler to use.
		:param name: Must be one of pdflatex, latex, xelatex, lualatex.
		:type name: str
		'''
		self.__latexCompiler = name or 'pdflatex'

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
		if isinstance(cli, list):
			self.__latexCLI = cli
		else:
			self.__latexCLI = re.split(r'\s+', cli, re.S)

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
		if isinstance(flags, list):
			self.__latexFlags = flags
		else:
			self.__latexFlags = re.split(r'\s+', flags, re.S)

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
		if isinstance(cli, list):
			self.__bibtexCLI = cli
		else:
			self.__bibtexCLI = re.split(r'\s+', cli, re.S)

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
		if isinstance(flags, list):
			self.__bibtexFlags = flags
		else:
			self.__bibtexFlags = re.split(r'\s+', flags, re.S)

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
		if isinstance(cli, list):
			self.__biberCLI = cli
		else:
			self.__biberCLI = re.split(r'\s+', cli, re.S)

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
		if isinstance(flags, list):
			self.__biberFlags = flags
		else:
			self.__biberFlags = re.split(r'\s+', flags, re.S)

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
		if isinstance(cli, list):
			self.__makeindexCLI = cli
		else:
			self.__makeindexCLI = re.split(r'\s+', cli, re.S)

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
		if isinstance(flags, list):
			self.__makeindexFlags = flags
		else:
			self.__makeindexFlags = re.split(r'\s+', flags, re.S)

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
		if isinstance(cli, list):
			self.__dvipsCLI = cli
		else:
			self.__dvipsCLI = re.split(r'\s+', cli, re.S)

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
		if isinstance(flags, list):
			self.__dvipsFlags = flags
		else:
			self.__dvipsFlags = re.split(r'\s+', flags, re.S)



