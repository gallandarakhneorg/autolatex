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
Tools that is extracting the dependencies of the TeX file.
'''

import os
import re

from autolatex2.tex import texparser
from autolatex2.tex import utils

class DependencyAnalyzer(texparser.Observer):
	'''
	Observer on TeX parsing for extracting the dependencies of the TeX file.
	'''

	__MACROS = {
		'input'							: '!{}',
		'include'						: '!{}',
		'makeindex'					: '',
		'printindex'					: '',
		'usepackage'					: '![]!{}',
		'RequirePackage'			: '![]!{}',
		'documentclass'			: '![]!{}',
		'addbibresource'			: '![]!{}',
		'makeglossaries'			: '',
		'printglossaries'		:'',
		'newglossaryentry'		:'![]!{}', 
	}

	def __init__(self, filename : str, rootDirectory : str):
		'''
		Constructor.
		:param filename: The name of the file to parse.
		:type filename: str
		:param rootDirectory: The name of the root directory.
		:type rootDirectory: str
		'''
		self.__isMultibib = False
		self.__isBibLaTeX = False
		self.__isBiber = False
		self.__isIndex = False
		self.__isXindy = False
		self.__isGlossary = False
		self.__dependencies = {}
		self.__filename = filename
		self.__basename = os.path.basename(os.path.splitext(filename)[0])
		self.__rootDirectory = rootDirectory

	@property
	def root_directory(self) -> str:
		'''
		Replies the root directory of the document.
		:return: The root directory of the document.
		:rtype: str
		'''
		return self.__rootDirectory

	@root_directory.setter
	def root_directory(self, d : str):
		'''
		Set the root directory of the document.
		:param d: The root directory of the document.
		:type d: str
		'''
		self.__rootDirectory = d

	@property
	def basename(self) -> str:
		'''
		Replies the basename of the document.
		:return: The basename  of the document.
		:rtype: str
		'''
		return self.__basename

	@basename.setter
	def basename(self, n : str):
		'''
		Set the basename of the document.
		:param d: The basename of the document.
		:type n: str
		'''
		self.__basename = n

	@property
	def filename(self) -> str:
		'''
		Replies the filename of the parsed file.
		:return: The filename of the parsed file.
		:rtype: str
		'''
		return self.__filename

	@filename.setter
	def filename(self, n : str):
		'''
		Set the filename of the parsed document.
		:param d: The filename of the parsed document.
		:type n: str
		'''
		self.__filename = n

	@property
	def is_multibib(self) -> bool:
		'''
		Replies the multibib support is enable
		:return: True if the multibib support is enabled.
		:rtype: bool
		'''
		return self.__isMultibib

	@is_multibib.setter
	def is_multibib(self, enable : bool) -> bool:
		'''
		Set if the multibib support is enable
		:param enable: True if the multibib support is enabled.
		:type enable: bool
		'''
		self.__isMultibib = enable

	@property
	def is_biblatex(self) -> bool:
		'''
		Replies the biblatex support is enable
		:return: True if the biblatex support is enabled.
		:rtype: bool
		'''
		return self.__isBibLaTeX

	@is_biblatex.setter
	def is_biblatex(self, enable : bool) -> bool:
		'''
		Set if the biblatex support is enable
		:param enable: True if the biblatex support is enabled.
		:type enable: bool
		'''
		self.__isBibLaTeX = enable

	@property
	def is_biber(self) -> bool:
		'''
		Replies the biber support is enable
		:return: True if the biber support is enabled.
		:rtype: bool
		'''
		return self.__isBiber

	@is_biber.setter
	def is_biber(self, enable : bool) -> bool:
		'''
		Set if the biber support is enable
		:param enable: True if the biber support is enabled.
		:type enable: bool
		'''
		self.__isBiber = enable

	@property
	def is_makeindex(self) -> bool:
		'''
		Replies the makeindex support is enable
		:return: True if the makeindex support is enabled.
		:rtype: bool
		'''
		return self.__isIndex

	@is_makeindex.setter
	def is_makeindex(self, enable : bool) -> bool:
		'''
		Set if the makeindex support is enable
		:param enable: True if the makeindex support is enabled.
		:type enable: bool
		'''
		self.__isIndex = enable

	@property
	def is_xindy_index(self) -> bool:
		'''
		Replies if the support for xindy support is enable.
		This flag is considered only if is_makeindex is enable.
		:return: True if the xindy support is enabled.
		:rtype: bool
		'''
		return self.__isXindy

	@is_xindy_index.setter
	def is_xindy_index(self, enable : bool) -> bool:
		'''
		Set if the support for xindy support is enable.
		This flag is considered only if is_makeindex is enable.
		:param enable: True if the xindy support is enabled.
		:type enable: bool
		'''
		self.__isXindy = enable

	@property
	def is_glossary(self) -> bool:
		'''
		Replies the glossary support is enable
		:return: True if the glossary support is enabled.
		:rtype: bool
		'''
		return self.__isGlossary

	@is_glossary.setter
	def is_glossary(self, enable : bool) -> bool:
		'''
		Set if the glossary support is enable
		:param enable: True if the glossary support is enabled.
		:type enable: bool
		'''
		self.__isGlossary = enable

	def __addDependency(self, dependencyType : str, dependencyFile : str):
		'''
		Add a dependency.
		:param dependencyType: The type of the dependency (tex, bib, ...)
		:type dependencyType: str
		:param dependencyFile: The filename.
		:type dependencyFile: str
		'''
		if dependencyType not in self.__dependencies:
			s = set()
			s.add(dependencyFile)
			self.__dependencies[dependencyType] = s
		else:
			self.__dependencies[dependencyType].add(dependencyFile)

	def getDependencyTypes(self) -> set:
		'''
		Replies the dependency types.
		:return: the set of dependency types.
		:rtype: set
		'''
		theSet = set(self.__dependencies.keys())
		if 'biblio' in theSet:
			theSet.remove('biblio')
		return theSet

	def getDependencies(self, dependencyType : str) -> set:
		'''
		Replies the dependencies of the given type.
		:param dependencyType: The type of the dependency (tex, bib, ...)
		:type dependencyType: str
		:return: the set of dependencies.
		:rtype: set
		'''
		if dependencyType in self.__dependencies:
			return self.__dependencies[dependencyType]
		return set()

	def getBibDependencies(self, bibType : str, bibDatabase : str = '') -> set:
		'''
		Replies the bibliography dependencies of the given type.
		:param bibType: The type of the dependency (bbx, ...)
		:type bibType: str
		:param bibDatabase: The name of the bibliography database.
		:type bibDatabase: str
		:return: the set of dependencies.
		:rtype: set
		'''
		if 'biblio' in self.__dependencies:
			hash1 = self.__dependencies['biblio']
			if bibDatabase in hash1:
				hash2 = hash1[bibDatabase]
				if bibType in hash2:
					return hash2[bibType]				
		return set()

	def getBibDataBases(self) -> set:
		'''
		Replies the set of bibliography databases
		:return: the set of bibliography database.
		:rtype: set
		'''
		if 'biblio' in self.__dependencies:
			hash1 = self.__dependencies['biblio']
			return hash1.keys()
		return set()

	def __addBibDependency(self, bibType : str, dependencyFile : str, dbName : str = ''):
		'''
		Add a dependency.
		:param bibType: The type of the dependency (bbx, ...)
		:type bibType: str
		:param dependencyFile: The filename.
		:type dependencyFile: str
		:param dbName: The name of the bibliography database (default: )
		:type dnName: str
		'''
		if 'biblio' not in self.__dependencies:
			hash1 = {}
			self.__dependencies['biblio'] = hash1
		else:
			hash1 = self.__dependencies['biblio']
		if dbName not in hash1:
			hash2 = {}
			hash1[dbName] = hash2
		else:
			hash2 = hash1[dbName]
		if bibType not in hash2:
			theSet = set()
			hash2[bibType] = theSet
		else:
			theSet = hash2[bibType]
		theSet.add(dependencyFile)

	def __parseBibReference(self, bibdb : str, *files : str):
		'''
		Add a dependency to a BibTeX database.
		:param bibdb: the BibTeX database.
		:type bibdb: str
		:param files: the BibTeX files.
		:type files: str
		'''
		for param in files:
			value = param['text']
			if value:
				for svalue in re.split('\s*,\s*', value):
					if svalue:
						if svalue.endswith('.bib'):
							bibFile = svalue
						else:
							bibFile = svalue + '.bib'
						if not os.path.isabs(bibFile):
							bibFile = os.path.join(self.root_directory, bibFile)
						if os.path.isfile(bibFile):
							self.__addBibDependency('bib', bibFile, bibdb)

	def expand(self, parser : texparser.Parser, rawtext : str, name : str, *parameter : texparser.Parameter) -> str:
		'''
		Expand the given macro on the given parameters.
		:param parser: reference to the parser.
		:type parser: Parser
		:param rawtext: The raw text that is the source of the expansion.
		:type rawtext: str
		:param name: Name of the macro.
		:type name: str
		:param parameter: Descriptions of the values passed to the TeX macro.
		:type parameter: Parameter
		:return: the result of the expand of the macro, or None to not replace the macro by something (the macro is used as-is)
		:rtype: str
		'''
		if name == '\\include' or name == '\\input':
			for param in parameter:
				value = param['text']
				if value:
					if utils.isTeXDocument(value):
						texFile = value
					else:
						texFile = value + utils.getTeXFileExtensions()[0]
					if not os.path.isabs(texFile):
						texFile = os.path.join(self.root_directory, texFile)
					if os.path.isfile(texFile):
						self.__addDependency('tex', texFile)
		elif name == '\\makeindex' or name == '\\printindex':
			self.is_makeindex = True
		elif name == '\\makeglossaries' or name == '\\printglossaries' or name == '\\newglossaryentry':
			self.is_glossary = True
		elif name == '\\usepackage' or name == '\\RequirePackage':
			sty = parameter[1]['text']
			if sty.endswith('.sty'):
				styFile = sty
			else:
				styFile = sty + ".sty"
			if styFile == 'multibib.sty':
				self.is_multibib = True
			elif styFile == 'biblatex.sty':
				self.is_biblatex = True
				# Parse the biblatex parameters
				if parameter[0] and parameter[0]['text']:
					params = re.split(r'\s*\,\s*', (parameter[0]['text'] or '').strip())
					for p in params:
						k = None
						v = None
						r = re.match(r'^([^=]+)\s*=\s*(.*?)\s*$', p, re.DOTALL)
						if r:
							k = r.group(1)
							v = r.group(2) or ''
						else:
							k = p
							v = ''
						if k == 'backend':
							self.is_biber = (v == 'biber')
						elif k == 'style':
							if v.endswith('.bbx'):
								bbxFile = v
							else:
								bbxFile = v + ".bbx"
							if not os.path.isabs(bbxFile):
								bbxFile = os.path.join(self.root_directory, bbxFile)
							if os.path.isfile(bbxFile):
								self.__addBibDependency('bbx', bbxFile)
							if v.endswith('.cbx'):
								cbxFile = v
							else:
								cbxFile = v + ".cbx"
							if not os.path.isabs(cbxFile):
								cbxFile = os.path.join(self.root_directory, cbxFile)
							if os.path.isfile(cbxFile):
								self.__addBibDependency('cbx', cbxFile)
						elif k == 'bibstyle':
							if v.endswith('.bbx'):
								bbxFile = v
							else:
								bbxFile = v + ".bbx"
							if not os.path.isabs(bbxFile):
								bbxFile = os.path.join(self.root_directory, bbxFile)
							if os.path.isfile(bbxFile):
								self.__addBibDependency('bbx', bbxFile)
						elif k == 'citestyle':
							if v.endswith('.cbx'):
								cbxFile = v
							else:
								cbxFile = v + '.cbx'
							if not os.path.isabs(cbxFile):
								cbxFile = os.path.join(self.root_directory, cbxFile)
							if os.path.isfile(cbxFile):
								self.__addBibDependency('cbx', cbxFile)
			elif styFile == 'indextools.sty':
				if parameter[0] and parameter[0]['text'] and 'xindy' in parameter[0]['text']:
					self.is_xindy_index = True
			elif styFile == 'glossaries.sty':
				self.is_glossary = True
			else:
				if not os.path.isabs(styFile):
					styFile = os.path.join(self.root_directory, styFile)
				if os.path.isfile(styFile):
					self.__addDependency('sty', styFile)
		elif name == '\\documentclass':
			cls = parameter[1]['text']
			if cls.endswith('.cls'):
				clsFile = cls
			else:
				clsFile = cls + '.cls'
			if not os.path.isabs(clsFile):
				clsFile = os.path.join(self.root_directory, clsFile)
			if os.path.isfile(clsFile):
				self.__addDependency('cls', clsFile)
		else:
			if name.startswith('\\bibliographystyle'):
				if not self.is_multibib:
					bibdb = self.basename
				else:
					bibdb = name[18:] if len(name) > 18 else self.basename
				for param in parameter:
					value = param['text']
					if value:
						for svalue in re.split('\s*,\s*',value.strip()):
							if svalue:
								if svalue.endswith('.bst'):
									bstFile = svalue
								else:
									bstFile = svalue + '.bst'
								if not os.path.isabs(bstFile):
									bstFile = os.path.join(self.root_directory, bstFile)
								if os.path.isfile(bstFile):
									self.__addBibDependency('bst', bstFile, bibdb)
			elif name.startswith('\\bibliography'):
				if not self.is_multibib:
					bibdb = self.basename
				else:
					bibdb = name[13:] if len(name) > 13 else self.basename
				self.__parseBibReference(bibdb, *parameter)
			elif name == '\\addbibresource':
				bibdb = self.basename
				self.__parseBibReference(bibdb, *parameter)
		return ''

	def findMacro(self, parser : texparser.Parser, name : str, special : bool, math : bool) -> str:
		'''
		Invoked each time a macro definition is not found in the parser data.
		:param parser: reference to the parser.
		:type parser: Parser
		:param name: Name of the macro.
		:type name: str
		:param special: Indicates if the macro is a special macro or not.
		:type special: bool
		:param math: Indicates if the math mode is active.
		:type math: bool
		:return: the definition of the macro, ie. the macro prototype. See the class documentation for an explanation about the format of the macro prototype.
		:rtype: str
		'''
		if not special:
			if name.startswith('bibliographystyle'):
				return '!{}'
			elif name.startswith('bibliography'):
				return '!{}'
		return None

	def run(self):
		'''
		Detect the dependencies.
		'''
		with open(self.filename) as f:
			content = f.read()

		parser = texparser.TeXParser()
		parser.observer = self
		parser.filename = self.filename

		for k, v in self.__MACROS.items():
			parser.add_text_mode_macro(k, v)
			parser.add_math_mode_macro(k, v)

		parser.parse(content)

