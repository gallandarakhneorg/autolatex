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

from autolatex2.cli.commands.view import MakerAction as extended_maker_action
from autolatex2.make.maketool import AutoLaTeXMaker

import gettext
_T = gettext.gettext

# Extends MakerAction from view module (alias extended_maker_action) in order
# to inherit from this super action.
class MakerAction(extended_maker_action):

	id = 'all'

	alias = 'default'

	help = _T('Performs all processing actions that are required to produce the PDF, DVI or Postscript and to view it with the specified PDF viewer if this option was enabled')

	def _internal_run_viewer(self,  maker : AutoLaTeXMaker,  args) -> bool:
		'''
		Run the internal viewer of the 'view' command.
		:param maker: the AutoLaTeX maker.
		:param args: the arguments.
		:return: True to continue process. False to stop the process.
		'''
		if self.configuration.view.view:
			return super()._internal_run_viewer(maker,  args)
		return True
