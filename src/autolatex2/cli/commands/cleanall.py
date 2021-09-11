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

from autolatex2.cli.commands.clean import MakerAction as extended_maker_action

import gettext
_T = gettext.gettext

class MakerAction(extended_maker_action):

	id = 'cleanall'
	
	alias = ['mrproper']

	help = _T('Extend the \'clean\' command by removing the backup files and the automatically generated images')

	def run(self,  args) -> bool:
		'''
		Callback for running the command.
		:param args: the arguments.
		:return: True if the process could continue. False if an error occurred and the process should stop.
		'''
		# Remove the tamporary files
		self.__nb_deletions = 0
		if not self.run_clean_command(args):
			return False
		if not self.run_cleanall_command(args):
			return False
		self._show_deletions_message(args)
		return True
