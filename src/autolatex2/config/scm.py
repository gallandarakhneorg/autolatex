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
Configuration for the SCM.
'''

import autolatex2.utils.utilfunctions as genutils

class ScmConfig(object):
	'''
	Configuration of a AutoLaTeX instance.
	'''

	def __init__(self):
		self.__commitCLI = list()
		self.__updateCLI = list()

	@property
	def commitCLI(self) -> list:
		'''
		Replies the command-line for commiting to the SCM system.
		:return: The CLI
		:rtype: list
		'''
		return self.__commitCLI

	@commitCLI.setter
	def commitCLI(self,  cli):
		'''
		Change the command-line for commiting to the SCM system.
		:return: The CLI
		:rtype: list or str
		'''
		if cli is None:
			self.__commitCLI = list()
		elif isinstance(cli,  list):
			self.__commitCLI = cli
		else:
			self.__commitCLI = genutils.parseCLI(cli)

	@property
	def updateCLI(self) -> list:
		'''
		Replies the command-line for updating the current folder from the SCM system.
		:return: The CLI
		:rtype: list
		'''
		return self.__updateCLI

	@updateCLI.setter
	def updateCLI(self,  cli):
		'''
		Change the command-line for updating the current folder from the SCM system.
		:return: The CLI
		:rtype: list or str
		'''
		if cli is None:
			self.__updateCLI = list()
		elif isinstance(cli,  list):
			self.__updateCLI = cli
		else:
			self.__updateCLI = genutils.parseCLI(cli)
