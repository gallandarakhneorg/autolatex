#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# autolatex/utils/gtk_utils.py
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

#---------------------------------
# IMPORTS
#---------------------------------

# Import standard python libs
from gi.repository import Gtk

def get_insert_index_dichotomic(list_store, column, data):
	f = 0
	l = list_store.iter_n_children(None) - 1
	while l >= f:
		c = (f+l) / 2
		path = Gtk.TreePath(c)
		d = list_store[path][column]
		cmpt = (data > d) - (data < d)
		if cmpt == 0:
			return -1
		elif cmpt < 0:
			l = c-1
		else:
			f = c+1
	return f

