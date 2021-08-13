#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 1998-2021  Stephane Galland <galland@arakhne.org>
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
Abstract implementation of an interpreter for the AutoLaTeX translators.
'''

import pprint
import abc

import gettext
_T = gettext.gettext

from autolatex2.utils.runner import *
from autolatex2.config.configobj import Config

######################################################################
##
class AbstractTranslatorInterpreter(Runner):
	'''
	Definition of an abstract implementation of an interpreter for the AutoLaTeX translators.
	'''

	def __init__(self,  configuration : Config):
		'''
		Construct an translator interpreter.
		:param configuration: The general configuration.
		:type configuration: Config
		'''
		self.__globalVariables = dict()
		self.__parent = None
		self.__configuration = configuration

	@property
	def configuration(self) -> Config:
		'''
		Replies the configuration.
		:return: The configuration.
		:rtype: Config
		'''
		return self.__configuration

	@configuration.setter
	def configuration(self, c : Config):
		'''
		Change the configuration.
		:param c: The configuration.
		:type c: Config
		'''
		self.__configuration = c

	@property
	def parent(self) -> object:
		'''
		Replies the parent interpreter.
		:return: The parent interpreter.
		:rtype: AbstractTranslatorInterpreter
		'''
		return self.__parent

	@parent.setter
	def parent(self, p : object):
		'''
		Change the parent interpreter.
		:param p: The parent interpreter, or None for unset it.
		:type p: AbstractTranslatorInterpreter
		'''
		self.__parent = p

	@property
	def globalVariables(self):
		'''
		Replies all the global variables.
		:return: the map of the global variables in which the keys are the variable names.
		:rtype: map
		'''
		return self.__globalVariables

	@property
	def runnable(self) -> bool:
		'''
		Replies if the interpreter is runnable, ie. the underground interpreter can be run.
		:return: True if the interpreter could be run.
		:rtype: bool
		'''
		raise NotImplementedError

	@property
	def interpreter(self) -> str:
		'''
		Replies the name of the interpreter.
		:return: The name of the interpreter.
		:rtype: str
		'''
		raise NotImplementedError

	@abc.abstractmethod
	def run(self, code : str):
		'''
		Run the interpreter.
		:param code: The Python code to interprete.
		:type code: str
		'''
		raise NotImplementedError

	@abc.abstractmethod
	def filterVariableName(self, name : str) -> str:
		'''
		Filter the name of the variable.
		:param name: The name to filter.
		:type name: str
		:return: The filtering result, that must be a valid name in the translator's language.
		:rtype: str
		'''
		raise NotImplementedError

	def toPython(self, value):
		'''
		Convert a value to a valid Python code.
		:param value: The value to convert.
		:type value: object
		'''
		pp = pprint.PrettyPrinter(indent=2)
		v = pp.pformat(value)
		return v


