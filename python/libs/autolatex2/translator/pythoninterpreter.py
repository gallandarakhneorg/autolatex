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

from autolatex2.translator.abstractinterpreter import AbstractTranslatorInterpreter

######################################################################
##
class TranslatorInterpreter(AbstractTranslatorInterpreter):
	'''
	Definition of a Python implementation of an interpreter for the AutoLaTeX translators.
	'''

	@property
	def runnable(self) -> bool:
		'''
		Replies if the interpreter is runnable, ie. the underground interpreter can be run.
		:return: True if the interpreter could be run.
		:rtype: bool
		'''
		return shutil.which('python') is not None

	
	@property
	def interpreter(self) -> str:
		'''
		Replies the name of the interpreter.
		:return: The name of the interpreter.
		:rtype: str
		'''
		return 'python'


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
		:param code: The Python code to interprete.
		:type code: str
		'''
		fullcode = "#!/usr/bin/env python3\n\n\n" + code
		variables = dict()
		for k, v in self.globalVariables.items():
			variables[self.filterVariableName(k)] = v
		return self.runPython(fullcode, False, variables)


