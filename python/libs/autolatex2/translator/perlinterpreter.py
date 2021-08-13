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
Perl implementation of an interpreter for the AutoLaTeX translators.
'''

import io
import pprint
import shutil

import gettext
_T = gettext.gettext

from autolatex2.translator.abstractinterpreter import AbstractTranslatorInterpreter
from autolatex2.config.configobj import Config

######################################################################
##
class TranslatorInterpreter(AbstractTranslatorInterpreter):
	'''
	Definition of a Perl implementation of an interpreter for the AutoLaTeX translators.
	'''

	def __init__(self,  configuration : Config):
		'''
		Construct an translator interpreter.
		:param configuration: The general configuration.
		:type configuration: Config
		'''
		super().__init__(configuration)

	@property
	def runnable(self) -> bool:
		'''
		Replies if the interpreter is runnable, ie. the underground interpreter can be run.
		:return: True if the interpreter could be run.
		:rtype: bool
		'''
		return shutil.which('perl') is not None

	
	@property
	def interpreter(self) -> str:
		'''
		Replies the name of the interpreter.
		:return: The name of the interpreter.
		:rtype: str
		'''
		return 'perl'


	def toPerl(self, value, inline : bool = True):
		'''
		Convert a value to Perl code.
		:param value: The value to convert.
		:type value: object
		:return: The Perl expression for the value.
		:rtype: str
		'''
		if isinstance(value, list):
			plist = list()
			for e in value:
				plist.append(self.toPerl(e, False))
			pvalue = ', '.join(plist)
			if inline:
				return "(" + pvalue + ")"
			else:
				return "[" + pvalue + "]"
		elif isinstance(value, set):
			plist = list()
			for e in value:
				plist.append(
					"%s => 1", self.toPerl(e, False))
			pvalue = ', '.join(plist)
			if inline:
				return "(" + pvalue + ")"
			else:
				return "[" + pvalue + "]"
		elif isinstance(value, dict):
			plist = list()
			for e in value:
				plist.append(
					"%s => %s", e, self.toPerl(value[e], False))
			pvalue = ', '.join(plist)
			if inline:
				return "(" + pvalue + ")"
			else:
				return "[" + pvalue + "]"
		else:
			pp = pprint.PrettyPrinter()
			v = pp.pformat(value)
			return str(v)

	def getPerlPrefix(self, value):
		'''
		Replies the perl variable prefix for the given value.
		:param value: The value to get the type for.
		:type value: object
		:return: The perl variable prefix.
		:rtype: str
		'''
		if isinstance(value, list):
			return '@'
		elif isinstance(value, set) or isinstance(value, dict):
			return '%'
		elif isinstance(value, io.IOBase):
			return '*'
		else:
			return '$'

	def filterVariableName(self, name : str) -> str:
		'''
		Filter the name of the variable.
		:param name: The name to filter.
		:type name: str
		:return: The filtering result, that must be a valid name in the translator's language.
		:rtype: str
		'''
		return name

	def run(self, code : str):
		'''
		Run the interpreter.
		:param code: The Perl code to interprete.
		:type code: str
		'''
		fullCode = "#!/usr/bin/env perl\n"
		for name in self.globalVariables:
			value = self.globalVariables[name]
			prefix = self.getPerlPrefix(value)
			pvalue = self.toPerl(value)
			fullCode += ("my %s%s = %s;\n" % (prefix, self.filterVariableName(name), pvalue))
		fullCode += "\n\n\n"+ code
		return self.runScript(fullCode, 'perl')


