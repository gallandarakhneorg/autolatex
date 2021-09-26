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
Configuration for the translators.
'''

from enum import IntEnum, unique

import gettext
_T = gettext.gettext


######################################################################
##
@unique
class TranslatorLevel(IntEnum):
	'''
	Level of execution of a translator.
	'''
	NEVER = -1
	SYSTEM = 0
	USER = 1
	DOCUMENT = 2

	def __str__(self):
		return _T(self.name.lower())


class TranslatorConfig(object):
	'''
	Configuration of the AutoLaTeX translators.
	'''

	def __init__(self):	
		self.__ignoreSystemTranslators = False
		self.__ignoreUserTranslators = False
		self.__ignoreDocumentTranslators = False
		self.__includePaths = list()
		self.__imagePaths = list()
		self.__imagesToConvert = set()
		self.__recursiveImagePath = True
		self.__inclusions = list((dict(), dict(), dict()))
		self.__is_translator_enable = True
		self.__enable_translatorfile_format_1 = False

	@property
	def is_translator_fileformat_1_enable(self) -> bool:
		'''
		Replies if the reading of the translators' fils in format 1 is activated.
		:rtype: bool
		'''
		return self.__enable_translatorfile_format_1

	@is_translator_fileformat_1_enable.setter
	def is_translator_fileformat_1_enable(self, enable : bool):
		'''
		Change the activation flag for the reading of the translators' fils in format 1.
		:type enable: bool
		'''
		self.__enable_translatorfile_format_1 = enable

	@property
	def is_translator_enable(self) -> bool:
		'''
		Replies if the translators are activated.
		:rtype: bool
		'''
		return self.__is_translator_enable

	@is_translator_enable.setter
	def is_translator_enable(self, enable : bool):
		'''
		Change the activation flag for the translators.
		:type enable: bool
		'''
		self.__is_translator_enable = enable

	@property
	def ignoreSystemTranslators(self) -> bool:
		return self.__ignoreSystemTranslators

	@ignoreSystemTranslators.setter
	def ignoreSystemTranslators(self, ignore : bool):
		self.__ignoreSystemTranslators = ignore

	@property
	def ignoreUserTranslators(self) -> bool:
		return self.__ignoreUserTranslators

	@ignoreUserTranslators.setter
	def ignoreUserTranslators(self, ignore : bool):
		self.__ignoreUserTranslators = ignore

	@property
	def ignoreDocumentTranslators(self) -> bool:
		return self.__ignoreDocumentTranslators

	@ignoreDocumentTranslators.setter
	def ignoreDocumentTranslators(self, ignore : bool):
		self.__ignoreDocumentTranslators = ignore

	@property
	def includePaths(self) -> list:
		'''
		Replies the inclusion paths for the translators.
		:rtype: list
		'''
		return self.__includePaths

	@includePaths.setter
	def includePaths(self, path : list) -> list:
		'''
		Set the inclusion paths for the translators.
		:param path: The inclusion paths.
		:type path: list
		'''
		if path is None:
			self.__includePaths = list()
		else:
			for p in path:
				if p is None:
					raise Exception(_T('Illegal None value for the include path'))
			self.__includePaths = path

	def addIncludePath(self,  path : str):
		'''
		Add a translator path for the translators.
		:param path: the path to add.
		:type path: str
		'''
		if path is None:
			raise Exception(_T('Illegal None value for the include path'))
		self.__includePaths.append(path)

	@property
	def imagePaths(self) -> list:
		'''
		Replies the image paths for the translators.
		:rtype: list
		'''
		return self.__imagePaths

	@imagePaths.setter
	def imagePaths(self, path : list):
		'''
		Set the image paths for the translators.
		:param path: The image paths.
		:type path: list
		'''
		self.__imagePaths = path

	def addImagePath(self,  path : str):
		'''
		Add an image path for the translators.
		:param path: the path to add.
		:type path: str
		'''
		self.__imagePaths.append(path)

	@property
	def imagesToConvert(self) -> set:
		'''
		Replies the images to convert that are manually specified.
		:rtype: set
		'''
		return self.__imagesToConvert

	@imagesToConvert.setter
	def imagesToConvert(self, images : set):
		'''
		Set manually the image to convert.
		:param images: The images.
		:type images: set
		'''
		self.__imagesToConvert = images

	def addImageToConvert(self,  img_path : str):
		'''
		Add an image to be converted.
		:param img_path: the path of the image to convert.
		:type img_path: str
		'''
		self.__imagesToConvert.add(img_path)

	@property
	def recursiveImagePath(self) -> bool:
		'''
		Replies if the image search is recursive in the directory tree.
		:rtype: bool
		'''
		return self.__recursiveImagePath

	@recursiveImagePath.setter
	def recursiveImagePath(self, recursive : bool):
		'''
		Set if the image search is recursive in the directory tree.
		:param recursive: True if recursive.
		:type recursive: bool
		'''
		self.__recursiveImagePath = recursive

	@property
	def inclusions(self) -> list:
		'''
		Replies the inclusion configuration.
		:return: The internal data structure for specifying the inclusions.
		:rtype: list
		'''
		return self.__inclusions

	def setIncluded(self, translator, level : TranslatorLevel, included : bool):
		'''
		Set if the given translator is marked as included in configuration.
		:param translator: The name of the translator.
		:type translator: str
		:param level: The level at which the inclusion must be considered (see TranslatorLevel enumeration).
		:type level: TranslatorLevel
		:param included: True if included. False if not included. None if not specified in the configuration.
		:type included: bool
		:
		'''
		if level is None or level == TranslatorLevel.NEVER:
			level = TranslatorLevel.SYSTEM
		if included is None:
			if translator in self.__inclusions[level.value]:
				del self.__inclusions[level.value][translator]
		else:
			self.__inclusions[level.value][translator] = included

	def included(self, translator : str, level : TranslatorLevel, inherit : bool = True) -> bool:
		'''
		Replies if the given translator is marked as included in configuration.
		:param translator: The name of the translator.
		:type translator: str
		:param level: The level at which the inclusion must be considered (see TranslatorLevel enumeration).
		:type level: TranslatorLevel
		:param inherit: Indicates if the inclusions of the lower levels are inherited. Default value: True.
		:type inherit: bool
		:return: The inclusion. True if included. False if not included. None if not specified in the configuration.
		:rtype: bool
		:
		'''
		if level is None or level == TranslatorLevel.NEVER or not translator:
			return None
		if inherit:
			# +1 because of the NEVER element at index 0
			# +1 because of the use of the range operator: [start_index:end_index+1]
			max_level = int(level.value) + 2
			lvls = list(TranslatorLevel)[1:max_level]
			for level in reversed(lvls):
				if translator in self.__inclusions[level.value] and self.__inclusions[level.value][translator] is not None:
					return self.__inclusions[level.value][translator]
		elif translator in self.__inclusions[level.value]:
			return self.__inclusions[level.value][translator]
		return None

	def inclusionLevel(self, translator : str) -> TranslatorLevel:
		'''
		Replies the highest level at which the translator is included.
		:param translator: The name of the translator.
		:type translator: str
		:return: The inclusion level (see TranslatorLevel enumeration) or None if not included or 'unspecified' if not specified.
		:rtype: TranslatorLevel
		:
		'''
		lvls = list(TranslatorLevel)[1:]
		for level in reversed(lvls):
			if translator in self.__inclusions[level.value] and self.__inclusions[level.value][translator] is not None:
				if self.__inclusions[level.value][translator]:
					return level
				else:
					return TranslatorLevel.NEVER
		return None

	def translators(self) -> dict:
		'''
		Replies the list of the registered translators with their inclusion status.
		:return: The pairs of translator names and inclusion status.
		:rtype: dict
		:
		'''
		trans = dict()
		lvls = list(TranslatorLevel)[1:]
		for level in reversed(lvls):
			for translator,  included in self.__inclusions[level].items():
				if translator not in trans and included is not None:
					trans[translator] = included
		return trans
