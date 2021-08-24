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
Configuration for the Cleaning feature.
'''

import os

class CleanConfig(object):
	'''
	Configuration of a AutoLaTeX instance.
	'''

	def __init__(self):
		self.__clean_files = list()
		self.__cleanall_files = list()

	@property
	def cleanFiles(self) -> list:
		'''
		Replies the list of files to clean.
		:rtype: list
		'''
		return self.__clean_files

	@cleanFiles.setter
	def cleanFiles(self,  files):
		'''
		Change the list of files to clean
		:return: The CLI
		:rtype: list or str
		'''
		if files is None:
			self.__clean_files = list()
		elif isinstance(files,  list):
			self.__clean_files = files
		else:
			self.__clean_files = files.split(os.pathsep)

	def addCleanFile(self,  file):
		'''
		Add a file to the list of files to clean
		:return: file name
		:rtype: str
		'''
		if file:
			self.__clean_files.append(file)

	@property
	def cleanallFiles(self) -> list:
		'''
		Replies the list of files to clean-all.
		:rtype: list
		'''
		return self.__cleanall_files

	@cleanallFiles.setter
	def cleanallFiles(self,  files):
		'''
		Change the list of files to clean-all
		:return: The CLI
		:rtype: list or str
		'''
		if files is None:
			self.__cleanall_files = list()
		elif isinstance(files,  list):
			self.__cleanall_files = files
		else:
			self.__cleanall_files = files.split(os.pathsep)

	def addCleanAllFile(self,  file):
		'''
		Add a file to the list of files to clean-all
		:return: file name
		:rtype: str
		'''
		if file:
			self.__cleanall_files.append(file)
