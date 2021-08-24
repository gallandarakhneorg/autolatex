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
Configuration for the viewer.
'''

import autolatex2.utils.utilfunctions as genutils

class ViewerConfig(object):
	'''
	Configuration of a AutoLaTeX instance.
	'''

	def __init__(self):
		self.__view_enable = False
		self.__viewerCLI = None
		self.__asyncview_enable = False

	@property
	def view(self) -> bool:
		'''
		Replies if the viewer is enable.
		:return: True if the viewer is enable.
		:rtype: bool
		'''
		return self.__view_enable

	@view.setter
	def view(self,  enable : bool):
		'''
		Change if the viewer is enable.
		:param enable: True if the viewer is enable.
		:type enable: bool
		'''
		self.__view_enable = enable

	@property
	def asyncview(self) -> bool:
		'''
		Replies if the asynchronous view is enable.
		:return: True if the async view is enable.
		:rtype: bool
		'''
		return self.__asyncview_enable

	@asyncview.setter
	def asyncview(self,  enable : bool):
		'''
		Change if the asynchronous view is enable.
		:param enable: True if the async view is enable.
		:type enable: bool
		'''
		self.__asyncview_enable = enable

	@property
	def viewerCLI(self) -> list:
		'''
		Replies the command-line for the viewer.
		:rtype: list
		'''
		return self.__viewerCLI

	@viewerCLI.setter
	def viewerCLI(self, cli):
		'''
		Set the command-line for the viewer.
		:type cli: str or list
		'''
		if cli is None:
			self.__viewerCLI = list()
		elif isinstance(cli, list):
			self.__viewerCLI = cli
		else:
			self.__viewerCLI = genutils.parseCLI(cli)

