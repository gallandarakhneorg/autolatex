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
Ruby implementation of an interpreter for the AutoLaTeX translators.
'''

import pprint
import shutil

from autolatex2.translator.interpreters.abstractinterpreter import AbstractTranslatorInterpreter
from autolatex2.config.configobj import Config

import gettext
_T = gettext.gettext

######################################################################
##
class TranslatorInterpreter(AbstractTranslatorInterpreter):
	'''
	Definition of a Ruby implementation of an interpreter for the AutoLaTeX translators.
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
		return shutil.which('ruby') is not None

	
	@property
	def interpreter(self) -> str:
		'''
		Replies the name of the interpreter.
		:return: The name of the interpreter.
		:rtype: str
		'''
		return 'ruby'


	def toRuby(self, value):
		'''
		Convert a value to Ruby code.
		:param value: The value to convert.
		:type value: object
		:return: The Ruby expression for the value.
		:rtype: str
		'''
		if isinstance(value, list) or isinstance(value, set):
			plist = list()
			for e in value:
				plist.append(self.toRuby(e, False))
			pvalue = ', '.join(plist)
			return "[" + pvalue + "]"
		elif isinstance(value, dict):
			plist = list()
			for e in value:
				plist.append(
					"%s => %s", e, self.toRuby(value[e], False))
			pvalue = ', '.join(plist)
			return "{" + pvalue + "}"
		else:
			pp = pprint.PrettyPrinter()
			v = pp.pformat(value)
			return str(v)

	def filterVariableName(self, name : str) -> str:
		'''
		Filter the name of the variable.
		:param name: The name to filter.
		:type name: str
		:return: The filtering result, that must be a valid name in the translator's language.
		:rtype: str
		'''
		return "_%s" % (name)

	def run(self, code : str):
		'''
		Run the interpreter.
		:param code: The Perl code to interprete.
		:type code: str
		'''
		fullCode = "#!/usr/bin/env ruby\n"
		for name in self.globalVariables:
			value = self.globalVariables[name]
			pvalue = self.toRuby(value)
			fullCode += ("%s = %s\n" % (self.filterVariableName(name), pvalue))
		fullCode += "\n\n\n"+ code
		return self.runScript(fullCode, 'ruby')


