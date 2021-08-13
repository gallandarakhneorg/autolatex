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
Javascript implementation of an interpreter for the AutoLaTeX translators.
'''

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
	Definition of a Javascript implementation of an interpreter for the AutoLaTeX translators.
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
		return shutil.which('js') is not None

	
	@property
	def interpreter(self) -> str:
		'''
		Replies the name of the interpreter.
		:return: The name of the interpreter.
		:rtype: str
		'''
		return 'javascript'


	def toJavascript(self, value):
		'''
		Convert a value to Javascript code.
		:param value: The value to convert.
		:type value: object
		:return: The Javascript expression for the value.
		:rtype: str
		'''
		if isinstance(value, list) or isinstance(value, set):
			plist = list()
			for e in value:
				plist.append(self.toJavascript(e, False))
			pvalue = ', '.join(plist)
			return "[" + pvalue + "]"
		elif isinstance(value, dict):
			raise RuntimeError["dictionary not supported"]
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
		:param code: The Javascript code to interprete.
		:type code: str
		'''
		fullCode = ""
		for name in self.globalVariables:
			value = self.filterVariableName(self.globalVariables[name])
			pvalue = self.toJavascript(value)
			fullCode += ("var %s = %s\n" % (name, pvalue))
		fullCode += "\n\n\n"+ code
		return self.runScript(fullCode, 'js')


