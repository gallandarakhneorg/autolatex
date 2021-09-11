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
Python implementation of an interpreter for the AutoLaTeX translators.
'''

import shutil
import re

from autolatex2.translator.interpreters.abstractinterpreter import AbstractTranslatorInterpreter
from autolatex2.config.configobj import Config

######################################################################
##
class TranslatorInterpreter(AbstractTranslatorInterpreter):
	'''
	Definition of a Python implementation of an interpreter for the AutoLaTeX translators.
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
		if self.configuration:
			cmd = self.configuration.pythonInterpreter
		else:
			cmd = 'python'
		return shutil.which(cmd) is not None

	
	@property
	def interpreter(self) -> str:
		'''
		Replies the name of the interpreter.
		:return: The name of the interpreter.
		:rtype: str
		'''
		if self.configuration:
			cmd = self.configuration.pythonInterpreter
		else:
			cmd = 'python'
		return cmd


	def filterVariableName(self, name : str) -> str:
		'''
		Filter the name of the variable.
		:param name: The name to filter.
		:type name: str
		:return: The filtering result, that must be a valid name in the translator's language.
		:rtype: str
		'''
		return "_%s" % (name.strip())

	def __find_line_prefix(self,  code_array : list) -> str:
		prefix = ''
		if code_array and len(code_array) > 0:
			m = re.match('^([ \t]+)',  code_array[0])
			if m:
				prefix = m.group(1)
		return prefix

	def __reformatCode(self,  code : str) -> str:
		code_array = code.rstrip().split("\n")
		prefix = self.__find_line_prefix(code_array)
		for i in range(len(code_array)):
			code_array[i] = code_array[i].replace(prefix,  '')
		return "\n".join(code_array)

	def run(self, code : str,  showScriptOnError : bool = True):
		'''
		Run the interpreter.
		:param code: The Python code to interprete.
		:type code: str
		:param showScriptOnError: Indicates if the script must be output on the standard error output in case of an error. Default is True.
		:type showScriptOnError: bool
		:return: A triplet containing the standard output, the
				 error output, and the error.
		:rtype: (str,str,exception)
		'''
		fullcode = "#!/usr/bin/env " + self.configuration.pythonInterpreter + "\n\n"
		fullcode = fullcode + "from autolatex2.utils.runner import Runner\n"
		if 'python_script_dependencies' in self.globalVariables and self.globalVariables['python_script_dependencies']:
			for dep in self.globalVariables['python_script_dependencies']:
				dep = str(dep).strip()
				if not dep.startswith('from ') and not dep.startswith('import '):
					fullcode = fullcode + 'import '
				fullcode = fullcode + dep
				fullcode = fullcode + "\n"
		fullcode = fullcode + "\n"
		fullcode = fullcode + self.__reformatCode(code)
		variables = dict()
		for k, v in self.globalVariables.items():
			variables[self.filterVariableName(k)] = v
		return self.runPython(fullcode, False, variables,  showScriptOnError)
