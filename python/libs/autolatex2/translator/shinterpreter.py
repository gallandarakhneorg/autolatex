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
Shell implementation of an interpreter for the AutoLaTeX translators.
'''

import io
import pprint
import shutil

import gettext
_T = gettext.gettext

from autolatex2.translator.abstractinterpreter import AbstractTranslatorInterpreter

######################################################################
##
class TranslatorInterpreter(AbstractTranslatorInterpreter):
	'''
	Definition of a Shell implementation of an interpreter for the AutoLaTeX translators.
	'''

	@property
	def runnable(self) -> bool:
		'''
		Replies if the interpreter is runnable, ie. the underground interpreter can be run.
		:return: True if the interpreter could be run.
		:rtype: bool
		'''
		return shutil.which('sh') is not None

	
	@property
	def interpreter(self) -> str:
		'''
		Replies the name of the interpreter.
		:return: The name of the interpreter.
		:rtype: str
		'''
		return 'sh'


	def toShellValue(self, value):
		'''
		Convert a value to Shell code.
		:param value: The value to convert.
		:type value: object
		:return: The Shell expression for the value.
		:rtype: str
		'''
		pp = pprint.PrettyPrinter()
		v = pp.pformat(value)
		return str(v)

	def toShell(self, name, value):
		'''
		Convert a value to Shell code.
		:param name: The name of the variable to set/unset.
		:type name: str
		:param value: The value to convert.
		:type value: object
		:return: The Shell expression for the value.
		:rtype: str
		'''
		if value is not None:
			if isinstance(value, list) or isinstance(value, set):
				plist = list()
				i = 0
				for e in value:
					plist.append("set %s[%d]=%s" % (name, i, self.toShellValue(e)))
					i = i + 1
				return '\n'.join(plist)
			elif isinstance(value, dict):
				raise RuntimeException["dictionary not supported"]
			else:
				return self.toShellValue(value)
		else:
			return "unset %s\n" % (name)

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
		:param code: The Shell code to interprete.
		:type code: str
		'''
		fullCode = "#!/usr/bin/env sh\n"
		for name in self.globalVariables:
			fullCode += self.toShell(self.filterVariableName(name), self.globalVariables[name])
		fullCode += "\n\n\n"+ code
		return self.runScript(fullCode, 'sh')


