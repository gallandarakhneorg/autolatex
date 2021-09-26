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
Readers of "transdef" files.
'''

import abc

from autolatex2.config.configobj import Config


class AbstractTransdefReader(object):
	'''
	Abstract implementation of a "transdef" reader.
	'''

	def __init__(self, configuration : Config):
		'''
		Contructor.
		:param configuration: the global configuration.
		:type configuration: Config
		'''
		self.__configuration = configuration

	@property
	def configuration(self):
		'''
		Replies the configuration.
		:return: the configuration.
		:rtype: Config
		'''
		return self.__configuration

	@configuration.setter
	def configuration(self,  c : Config):
		'''
		Change the configuration.
		:param c: the configuration.
		:type c: Config
		'''
		self.__configuration = c

	@abc.abstractmethod
	def readTranslatorFile(self, filename : str) -> dict:
		'''
		Read the translator file. The replied value is the set of keys read from the transdef file. Each value is a TransdefLine.
		:param filename: the name of the file to read.
		:type filename: str
		:rtype: dict
		'''
		pass
