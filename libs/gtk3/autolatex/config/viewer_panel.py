#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2013-14  Stephane Galland <galland@arakhne.org>
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

# Include the Glib, Gtk and Gedit libraries
from gi.repository import GObject, Gdk, Gtk, GdkPixbuf
# AutoLaTeX internal libs
from ..utils import utils
from . import abstract_panel

#---------------------------------
# INTERNATIONALIZATION
#---------------------------------

import gettext
_T = gettext.gettext

#---------------------------------
# CLASS Panel
#---------------------------------

# Gtk panel that is managing the configuration of the viewer
class Panel(abstract_panel.AbstractPanel):
  __gtype_name__ = "AutoLaTeXViewerPanel"

  def __init__(self, is_document_level, directory, window):
    abstract_panel.AbstractPanel.__init__(self, is_document_level, directory, window)

  #
  # Fill the grid
  #
  def _init_widgets(self):
    # Launch the viewer
    self._ui_launch_viewer_checkbox = self._create_switch(
        _T("Launch a viewer after compilation"))[1]
    # Viewer command line
    self._ui_viewer_command_field = self._create_entry(
        _T("Command for launching the viewer (optional)"))[1]


  #
  # Initialize the content
  #
  def _init_content(self):
    self._read_settings('viewer')
    #
    inh = self._get_settings_bool_inh('view')
    cur = self._get_settings_bool('view')
    self._init_overriding(self._ui_launch_viewer_checkbox, cur is not None)
    self._ui_launch_viewer_checkbox.set_active(utils.first_of(cur, inh, False))
    #
    inh = self._get_settings_str_inh('viewer')
    cur = self._get_settings_str('viewer')
    self._init_overriding(self._ui_viewer_command_field, cur is not None)
    self._ui_viewer_command_field.set_text(utils.first_of(cur, inh, ''))


  #
  # Connect signals
  #
  def _connect_signals(self):
    self._ui_launch_viewer_checkbox.connect('notify::active',self.on_launch_viewer_toggled)




  # Change the state of the widgets according to the state of other widgets
  def update_widget_states(self):
    is_active = self._ui_launch_viewer_checkbox.get_active()
    if not self._get_overriding(self._ui_launch_viewer_checkbox):
      inh = self._get_settings_bool_inh('view', False)
      if (inh!=is_active):
        GObject.idle_add(self._ui_launch_viewer_checkbox.set_active, inh)
        is_active = inh
    self._update_sentitivity(self._ui_viewer_command_field, is_active)
      

  # Invoke when the flag 'launch viewer' has changed
  def on_launch_viewer_toggled(self, widget, data=None):
    self.update_widget_states()

  # Invoked when the changes in the panel must be saved
  def save(self):
    self._reset_settings_section()
    #
    if self._get_sentitivity(self._ui_launch_viewer_checkbox):
      v = self._ui_launch_viewer_checkbox.get_active()
    else:
      v = None
    self._set_settings_bool('view', v)
    #
    if self._get_sentitivity(self._ui_viewer_command_field):
      v = self._ui_viewer_command_field.get_text()
    else:
      v = None
    self._set_settings_str('viewer', v)
    #
    return utils.backend_set_configuration(self._directory,
      'project' if self._is_document_level else 'user', self._settings)

