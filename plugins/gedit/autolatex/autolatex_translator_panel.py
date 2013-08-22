# autolatex - autolatex_translator_panel.py
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

# Include the Glib, Gtk and Gedit libraries
from gi.repository import GObject, Gdk, Gtk, GdkPixbuf
# AutoLaTeX internal libs
import autolatex_utils as utils

#---------------------------------
# INTERNATIONALIZATION
#---------------------------------

import gettext
_T = gettext.gettext

#---------------------------------
# CLASS IconType
#---------------------------------

class IconType:
    INHERITED = 0
    INCLUDED = 1
    EXCLUDED = 2
    INHERITED_CONFLICT = 3
    CONFLICT = 4

#---------------------------------
# CLASS IconType
#---------------------------------

class Level:
    SYSTEM = 0
    USER = 1
    PROJECT = 2

#---------------------------------
# CLASS Panel
#---------------------------------

# Gtk panel that is managing the configuration of the translators
class Panel(Gtk.Table):
	__gtype_name__ = "AutoLaTeXTranslatorPanel"

	def __init__(self, isDocumentLevel, directory):
		Gtk.Table.__init__(self,
				2, #rows
				2, #columns
				False) #non uniform
		self._directory = directory
		self._is_document_level = isDocumentLevel
		self._preload_icons()
		# Top label
		self._ui_label = Gtk.Label(_T("List of available translators:\n(click on the second column to change the loading state of the translators)"))
		self._ui_label.set_alignment(0, 0.5)
		self.attach(self._ui_label, 
				0,1,0,1, # left, right, top and bottom columns
				Gtk.AttachOptions.EXPAND, Gtk.AttachOptions.SHRINK, # x and y options
				0,0) # horizontal and vertical paddings
		# List of translators
		self._ui_translator_list = Gtk.ListStore(
						GdkPixbuf.Pixbuf.__gtype__, GdkPixbuf.Pixbuf.__gtype__,
						str, str)
		self._ui_translator_list_widget = Gtk.TreeView()
		self._ui_translator_list_widget.set_model(self._ui_translator_list)
		if isDocumentLevel:
			label1 = _T('usr')
			self._clickable_column_label = _T('doc')
		else:
			label1 = 'sys'
			self._clickable_column_label = _T('usr')
		column = Gtk.TreeViewColumn(label1, Gtk.CellRendererPixbuf(), pixbuf=0)
		self._ui_translator_list_widget.append_column(column)
		column = Gtk.TreeViewColumn(self._clickable_column_label, Gtk.CellRendererPixbuf(), pixbuf=1)
		self._ui_translator_list_widget.append_column(column)
		column = Gtk.TreeViewColumn(_T("name"), Gtk.CellRendererText(), text=2)
		self._ui_translator_list_widget.append_column(column)
		column = Gtk.TreeViewColumn(_T("description"), Gtk.CellRendererText(), text=3)
		self._ui_translator_list_widget.append_column(column)
		self._ui_translator_list_widget.set_headers_clickable(False)
		self._ui_translator_list_widget.set_headers_visible(True)
		# Scrolling pane for translator list
		self._ui_translator_list_scroll = Gtk.ScrolledWindow()
		self._ui_translator_list_scroll.add(self._ui_translator_list_widget)
		self._ui_translator_list_scroll.set_size_request(500,400)
		self._ui_translator_list_scroll.set_policy(Gtk.PolicyType.AUTOMATIC,Gtk.PolicyType.AUTOMATIC)
		self._ui_translator_list_scroll.set_shadow_type(Gtk.ShadowType.IN)
		self.attach (self._ui_translator_list_scroll, 
					0,1,1,2, # left, right, top and bottom columns
					Gtk.AttachOptions.FILL|Gtk.AttachOptions.EXPAND, # x option
					Gtk.AttachOptions.FILL|Gtk.AttachOptions.EXPAND, # y option
					5,5) # horizontal and vertical paddings
		# Management buttons
		self._ui_left_toolbar = Gtk.VButtonBox()
		self._ui_left_toolbar.set_layout(Gtk.ButtonBoxStyle.START)
		self.attach(self._ui_left_toolbar, 
					1,2,0,2, # left, right, top and bottom columns
					Gtk.AttachOptions.SHRINK, # x option
					Gtk.AttachOptions.FILL|Gtk.AttachOptions.EXPAND, # y option
					5,5) # horizontal and vertical paddings
		# Help
		#self._ui_left_toolbar.add (Gtk.HSeparator())
		if self._is_document_level:
			label1 = _T('Current user')
			label2 = _T('Current document')
		else:
			label1 = _T('All users')
			label2 = _T('Current user')
		self._ui_left_toolbar.add(self._make_legend(self._get_level_icon(0), label1))
		self._ui_left_toolbar.add(self._make_legend(self._get_level_icon(1), label2))
		self._ui_left_toolbar.add(Gtk.HSeparator())
		self._ui_left_toolbar.add(self._make_legend(self._get_level_icon(1), _T('Loaded, no conflict')))
		self._ui_left_toolbar.add(self._make_legend(self._get_level_icon(1, IconType.CONFLICT), _T('Loaded, conflict')))
		self._ui_left_toolbar.add(self._make_legend(self._get_level_icon(1, IconType.EXCLUDED), _T('Not loaded')))
		self._ui_left_toolbar.add(self._make_legend(self._get_level_icon(1, IconType.INHERITED), _T('Unspecified, no conflict')))
		self._ui_left_toolbar.add(self._make_legend(self._get_level_icon(1, IconType.INHERITED_CONFLICT), _T('Unspecified, conflict')))
		#
		# Initialize the panel
		#
		if self._is_document_level:
			left_level = Level.USER
			right_level = Level.PROJECT
		else:
			left_level = Level.SYSTEM
			right_level = Level.USER
		# Get the data from the backend
		self._translator_config = utils.backend_get_translators(self._directory)
		self._load_config = utils.backend_get_loads(self._directory)
		# Build the conflict map and the inclusion states
		self._translator_conflict_candidates = {}
		self._translator_inclusions_constants = {}
		self._translator_inclusions = {}
		for translator in self._translator_config.sections():
			source = self._translator_config.get(translator, 'full-source')
			if source not in self._translator_conflict_candidates:
				self._translator_conflict_candidates[source] = []
			self._translator_conflict_candidates[source].append(translator)
			self._translator_inclusions_constants[translator] = self._compute_inclusion_state(translator, left_level, right_level)
			self._translator_inclusions[translator] = self._compute_inclusion_state(translator, right_level, right_level)
		# Detect initial conflicts
		for translator in self._translator_config.sections():
			self._update_translator_states(translator)
		# Fill the table
		self._translator_indexes = {}
		index = 0
		for translator in self._translator_config.sections():
			human_readable = self._translator_config.get(translator, 'human-readable')
			icon1 = self._get_level_icon(0, self._translator_inclusions_constants[translator])
			icon2 = self._get_level_icon(1, self._translator_inclusions[translator])
			self._ui_translator_list.append( [ icon1, icon2, translator, human_readable ] )
			self._translator_indexes[translator] = index
			index = index + 1
		# Connect the UI events
		self._ui_translator_list_widget.connect('button-press-event', self.on_list_click_action);

	# Preloading the states' icons
	def _preload_icons(self):
		if self._is_document_level:
			left_level = Level.USER
			right_level = Level.PROJECT
		else:
			left_level = Level.SYSTEM
			right_level = Level.USER
		# Preload icons
		self._preloaded_icons = [[None,None,None,None,None],[None,None,None,None,None]]
		for i in range(5):
			self._preloaded_icons[0][i] = self.__get_level_icon(left_level, i)
			self._preloaded_icons[1][i] = self.__get_level_icon(right_level, i)

	# Load the bitmap of an icon
	def __get_level_icon(self, level, icon_type=IconType.INCLUDED):
		if level == Level.SYSTEM:
			icon_name = 'systemLevel'
		elif level == Level.USER:
			icon_name = 'userLevel'
		else:
			icon_name = 'projectLevel'
		
		if icon_type == IconType.INHERITED_CONFLICT:
			icon_name = icon_name + '_uc'
		elif icon_type == IconType.INHERITED:
			icon_name = icon_name + '_u'
		elif icon_type == IconType.CONFLICT:
			icon_name = icon_name + '_c'
		elif icon_type == IconType.EXCLUDED:
			icon_name = icon_name + '_ko'
		icon_name = icon_name + '.png'
		return GdkPixbuf.Pixbuf.new_from_file(utils.make_table_icon_path(icon_name))

	# Replies an icon
	def _get_level_icon(self, column, icon_type=IconType.INCLUDED):
		return self._preloaded_icons[column][int(icon_type)]

	# Utility function  to create the "help" legend
	def _make_legend(self, icon, label, top_padding=0):
		legend_alignment = Gtk.Table(5,2)
		icon_label = Gtk.Image.new_from_pixbuf(icon)
		legend_alignment.attach(icon_label, 0, 1, 0, 1,
					Gtk.AttachOptions.FILL, Gtk.AttachOptions.FILL,
					0, top_padding)
		text = Gtk.Label(label)
		text.set_alignment(0, 0.5)
		legend_alignment.attach(text, 1, 2, 0, 1,
					Gtk.AttachOptions.FILL, Gtk.AttachOptions.FILL,
					5, top_padding)
		return legend_alignment

	# Replies if the given translator, in the given state, may be assumed as included
	def _is_includable_with(self, translator, state):
		if state == IconType.INHERITED:
			state = self._translator_inclusions_constants[translator]
		elif state == IconType.INHERITED_CONFLICT:
			state = self._add_conflict_in_state(self._translator_inclusions_constants[translator])
		if state == IconType.INCLUDED or state == IconType.CONFLICT:
			return 1 # Sure, it is included
		if state == IconType.EXCLUDED:
			return 0 # Sure, it is not included
		return -1 # Don't know

	# Detect a conflict for the given translator, and update
	# the states of all the translators in the same group
	def _update_translator_states(self, translator):
		translators_to_update = []
		inclusion_state = self._translator_inclusions[translator]
		if inclusion_state != IconType.EXCLUDED:
			# Detect any conflict
			is_includable = self._is_includable_with(translator, inclusion_state)
			source = self._translator_config.get(translator, 'full-source')
			for candidate in self._translator_conflict_candidates[source]:
				if translator != candidate:
					other_state = self._translator_inclusions[candidate]
					is_other_includable = self._is_includable_with(candidate, other_state)
					if is_includable and is_other_includable:
						inclusion_state = self._add_conflict_in_state(inclusion_state)
			# change the state of the other translators
			if inclusion_state == IconType.CONFLICT or inclusion_state == IconType.INHERITED_CONFLICT:
				for candidate in self._translator_conflict_candidates[source]:
					if translator != candidate:
						other_state = self._translator_inclusions[candidate]
						new_other_state = self._add_conflict_in_state(other_state)
						if other_state!=new_other_state:
							self._translator_inclusions[candidate] = new_other_state
							translators_to_update.append(candidate)
		self._translator_inclusions[translator] = inclusion_state
		for translator in translators_to_update:
			self._update_translator_states(translator)
		return inclusion_state

	# Compute the state of a translator for the given level
	def _compute_inclusion_state(self, translator, query_level, editable_level):
		flag = IconType.INHERITED
		if query_level < editable_level:
			if self._load_config.has_option('system', translator):
				flag = IconType.INCLUDED if self._load_config.getboolean('system', translator) else IconType.EXCLUDED
			if query_level > Level.SYSTEM:
				if self._load_config.has_option('user', translator):
					flag = IconType.INCLUDED if self._load_config.getboolean('user', translator) else IconType.EXCLUDED
				if query_level > Level.USER:
					if self._load_config.has_option('project', translator):
						flag = IconType.INCLUDED if self._load_config.getboolean('project', translator) else IconType.EXCLUDED
		elif query_level == Level.SYSTEM:
			if self._load_config.has_option('system', translator):
				flag = IconType.INCLUDED if self._load_config.getboolean('system', translator) else IconType.EXCLUDED
		elif query_level == Level.USER:
			if self._load_config.has_option('user', translator):
				flag = IconType.INCLUDED if self._load_config.getboolean('user', translator) else IconType.EXCLUDED
		else:
			if self._load_config.has_option('project', translator):
				flag = IconType.INCLUDED if self._load_config.getboolean('project', translator) else IconType.EXCLUDED
		return flag

	# Translate the state by removing the conflict flag
	def _remove_conflict_in_state(self, state):
		if state == IconType.CONFLICT:
			return IconType.INCLUDED
		elif state == IconType.INHERITED_CONFLICT:
			return IconType.INHERITED
		return state
		
	# Translate the state by adding the conflict flag
	def _add_conflict_in_state(self, state):
		if state == IconType.INCLUDED:
			return IconType.CONFLICT
		elif state == IconType.INHERITED:
			return IconType.INHERITED_CONFLICT
		return state

	# Callback for changing the state of a translator
	def on_list_click_action(self, action, data=None):
		x, y = data.get_coords() #Gdk.Event
		path, column, cell_x, cell_y = action.get_path_at_pos(x,y)
		if path:
			title = column.get_title()
			if title == self._clickable_column_label:
				list_iter = self._ui_translator_list.get_iter(path)
				translator = self._ui_translator_list[list_iter][2]
				inclusion_state = self._translator_inclusions[translator]
				inclusion_state = self._remove_conflict_in_state(inclusion_state)
				# Move up
				inclusion_state = (inclusion_state + 1) % 3
				# Reset the states for the group
				source = self._translator_config.get(translator, 'full-source')
				for candidate in self._translator_conflict_candidates[source]:
					if translator != candidate:
						other_state = self._translator_inclusions[candidate]
						other_state = self._remove_conflict_in_state(other_state)
						self._translator_inclusions[candidate] = other_state
				self._translator_inclusions[translator] = inclusion_state
				# Detect conflicts in the group
				for candidate in self._translator_conflict_candidates[source]:
					self._update_translator_states(candidate)
				# Update the UI
				for translator in self._translator_conflict_candidates[source]:
					inclusion_state = self._translator_inclusions[translator]
					index = self._translator_indexes[translator]
					path = Gtk.TreePath(index)
					list_iter = self._ui_translator_list.get_iter(path)
					self._ui_translator_list[list_iter][1] = self._get_level_icon(1, inclusion_state)

	# Invoked when the changes in the panel must be saved
	def save(self):
		if self._is_document_level:
			section_name = 'project'
		else:
			section_name = 'user'
		self._load_config.remove_section(section_name)
		self._load_config.add_section(section_name)
		for translator in self._translator_inclusions:
			state = self._translator_inclusions[translator]
			if state == IconType.INCLUDED or state == IconType.CONFLICT:
				self._load_config.set(section_name, translator, 'true')
			elif state == IconType.EXCLUDED:
				self._load_config.set(section_name, translator, 'false')
		return utils.backend_set_loads(self._directory, self._load_config)
