#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# autolatex/__init__.py
# Copyright (C) 2013  Stephane Galland <galland@arakhne.org>
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

import os
import sublime
from utils import utils

__all__ = [ ]

_search_path = []
_root = sublime.packages_path()
if _root:
	_search_path.append(_root)
	for _directory in os.listdir(_root):
		_full = os.path.join(_root, _directory)
		if os.path.isdir(_full):
			_search_path.append(_full)

utils.init_plugin_configuration(
	__file__,
	'sublime-text-2-autolatex',
	_search_path)

