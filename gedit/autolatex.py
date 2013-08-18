# autolatex - autolatex.py
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
import os
import subprocess
import tempfile
# Try to use the threading library if it is available
try:
    import threading as _threading
except ImportError:
    import dummy_threading as _threading
# Include the Glib, Gtk and Gedit libraries
from gi.repository import GObject, Gtk, Gio, GdkPixbuf, Gedit

#---------------------------------
# CONSTANTS
#---------------------------------

# Level of verbosity of AutoLaTeX
DEFAULT_LOG_LEVEL = '--quiet'
# Binary file of AutoLaTeX
AUTOLATEX_BINARY = '/home/sgalland/git/autolatex/autolatex.pl'
# Path where the icons are installed
ICON_PATH = os.path.join(os.path.dirname(__file__), 'icons')

#---------------------------------
# DEFINITION OF THE GTK CONTRIBUTIONS
#---------------------------------
UI_XML = """<ui>
<menubar name="MenuBar">
    <menu name="ToolsMenu" action="Tools">
      <placeholder name="ToolsOps_3">
	<menu name="AutoLaTeXMenu" action="AutoLaTeXMenu">
	  <menuitem name="AutoLaTeXGenerateImageAction" action="AutoLaTeXGenerateImageAction"/>
	  <menuitem name="AutoLaTeXCompileAction" action="AutoLaTeXCompileAction"/>
	  <separator />
	  <menuitem name="AutoLaTeXCleanAction" action="AutoLaTeXCleanAction"/>
	  <menuitem name="AutoLaTeXCleanallAction" action="AutoLaTeXCleanallAction"/>
	  <separator />
	  <menuitem name="AutoLaTeXViewAction" action="AutoLaTeXViewAction"/>
	  <separator />
	  <menuitem name="AutoLaTeXDocumentConfAction" action="AutoLaTeXDocumentConfAction"/>
	  <menuitem name="AutoLaTeXUserConfAction" action="AutoLaTeXUserConfAction"/>
        </menu>
      </placeholder>
    </menu>
</menubar>
<toolbar name="ToolBar">
    <separator/>
    <toolitem name="AutoLaTeXCompileAction" action="AutoLaTeXCompileAction"/>
    <toolitem name="AutoLaTeXCleanAction" action="AutoLaTeXCleanAction"/>
    <toolitem name="AutoLaTeXViewAction" action="AutoLaTeXViewAction"/>
</toolbar>
</ui>"""

#---------------------------------
# CLASS AutoLaTeXExecutionThread
#---------------------------------

# Launch AutoLaTeX inside a thread, and wait for the result
class AutoLaTeXExecutionThread(_threading.Thread):
    # caller is an instance of AutoLaTeXPlugin
    # directory is the path to set as the current path
    # directive is the AutoLaTeX command
    # params are the CLI options for AutoLaTeX
    def __init__(self, caller, directory, directive, params):
	_threading.Thread.__init__(self)
	self.daemon = True
	self._caller = caller
	self._directory = directory
	self._cmd = [AUTOLATEX_BINARY] + params + [directive]

    # Run the thread
    def run(self):
	os.chdir(self._directory)
	process = subprocess.Popen(self._cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	output = ''
	if process:
	    out, err = process.communicate()
	    retcode = process.returncode
	    if retcode != 0:
		output = out + err
	# Update the UI for the inside of the Gtk thread
	GObject.idle_add(self._caller._update_action_validity, True, output)

#---------------------------------
# CLASS AutoLaTeXPlugin
#---------------------------------

# Plugin for Gedit
class AutoLaTeXPlugin(GObject.Object, Gedit.WindowActivatable):
    __gtype_name__ = "AutoLaTeXPlugin"
    window = GObject.property(type=Gedit.Window)
    
    #Constructor
    def __init__(self):
        GObject.Object.__init__(self)
	self._compilation_under_progress = False # Indicate if the compilation is under progress
	self._console_icon = None # Icon of the error console
	self._error_console = None # Current instance of the error console

    # Invoke when the plugin is activated 
    def do_activate(self):
	self._console_icon = self._get_icon('console')
        self._add_ui()

    # Invoke when the plugin is desactivated
    def do_deactivate(self):
        self._remove_ui()

    # Invoke when the UI is updated
    def do_update_state(self):
	# Change the sentitivity of the Gtk actions
	doc = self._find_AutoLaTeX_dir()
	hasDocument = (doc!=None)
	if self._document_actions:
            self._document_actions.set_sensitive(hasDocument
			and not self._compilation_under_progress)
	if self._texsensitive_actions:
            self._texsensitive_actions.set_sensitive(self._is_TeX_document()
			and not self._compilation_under_progress)

    # Update the UI according to the flag "compilation under progress"
    # and to compilation outputs
    def _update_action_validity(self, valid, console_content):
	# Display or hide the error console if an error message is given or not
	if (console_content):
		if (not self._error_console or self._error_console.get_parent == None):
			if (not self._error_console):
				self._error_console = Gtk.TextView()
				self._error_console.set_editable(False)
				self._error_console.set_hscroll_policy(Gtk.ScrollablePolicy.NATURAL)
				self._error_console.set_vscroll_policy(Gtk.ScrollablePolicy.NATURAL)
			panel = self.window.get_bottom_panel()
			panel.add_item(self._error_console,
				"autolatex-console-panel",
				"AutoLaTeX Console",
				Gtk.Image.new_from_pixbuf(self._console_icon))
		self._error_console.get_buffer().set_text(console_content)
	        panel.activate_item(self._error_console)
		if panel.get_property("visible") == False:
                        panel.set_property("visible", True)
	else:
		if (self._error_console):
			panel = self.window.get_bottom_panel()
			panel.remove_item(self._error_console)
			self._error_console = None
	# Update the sensitivities of the Widgets
	self._compilation_under_progress = not valid
	self.do_update_state()    

    # Load an icon from the AutoLaTeX package
    def _get_icon(self, icon):
	iconfile = os.path.join(ICON_PATH, '24', 'autolatex-'+icon+'.png')
	return GdkPixbuf.Pixbuf.new_from_file(iconfile)


    # Add any contribution to the Gtk UI
    def _add_ui(self):
	# Get the UI manager
        manager = self.window.get_ui_manager()
	# Create the Top menu for AutoLaTeX
        self._menu = Gtk.ActionGroup("AutoLaTeXMenu")
        self._menu.add_actions([
            ('AutoLaTeXMenu', None, "AutoLaTeX", 
                None, "AutoLaTeX", 
                None),
        ])
        manager.insert_action_group(self._menu)
	# Create the group of actions that are needing an AutoLaTeX document
        self._document_actions = Gtk.ActionGroup("AutoLaTeXDocumentActions")
        self._document_actions.add_actions([
	    ('AutoLaTeXGenerateImageAction', None, "Generate images", 
                None, "Generate the images with AutoLaTeX", 
                self.on_generateimage_action_activate),
            ('AutoLaTeXCompileAction', None, "Compile", 
                '<shift><ctrl>R', "Compile with AutoLaTeX", 
                self.on_compile_action_activate),
            ('AutoLaTeXCleanAction', None, "Remove temporary files", 
                None, "Clean with AutoLaTeX", 
                self.on_clean_action_activate),
            ('AutoLaTeXCleanallAction', None, "Clean all", 
                '<shift><ctrl>C', "Clean all with AutoLaTeX", 
                self.on_cleanall_action_activate),
            ('AutoLaTeXViewAction', None, "View the PDF", 
                None, "Open the PDF viewer", 
                self.on_view_action_activate),
        ])
        manager.insert_action_group(self._document_actions)
	# Create the group of actions that are needing an TeX document
        self._texsensitive_actions = Gtk.ActionGroup("AutoLaTeXTeXSensitiveActions")
        self._texsensitive_actions.add_actions([
            ('AutoLaTeXDocumentConfAction', None, "Document configuration", 
                None, "Change the configuration for the document", 
                self.on_document_configuration_action_activate),
        ])
        manager.insert_action_group(self._texsensitive_actions)
	# Create the group of actions that are not needing any special document
        self._general_actions = Gtk.ActionGroup("AutoLaTeXGeneralActions")
        self._general_actions.add_actions([
            ('AutoLaTeXUserConfAction', None, "User configuration", 
                None, "Change the configuration for the user", 
                self.on_user_configuration_action_activate),
        ])
        manager.insert_action_group(self._general_actions)
	# Put the icons into the actions
	for definition in [	(self._document_actions, 'AutoLaTeXGenerateImageAction', 'images'),
				(self._document_actions, 'AutoLaTeXCompileAction', 'compile'),
				(self._document_actions, 'AutoLaTeXCleanAction', 'clean'),
				(self._document_actions, 'AutoLaTeXCleanallAction', 'cleanall'),
				(self._document_actions, 'AutoLaTeXViewAction', 'view'),
				(self._texsensitive_actions, 'AutoLaTeXDocumentConfAction', 'preferences'),
				(self._general_actions, 'AutoLaTeXUserConfAction', 'preferences')
			]:
		action = definition[0].get_action(definition[1])
		action.set_gicon(self._get_icon(definition[2]))
	# Add the Gtk contributions
        self._ui_merge_id = manager.add_ui_from_string(UI_XML)
        manager.ensure_update()
        
    # Remove all contributions to the Gtk UI
    def _remove_ui(self):
	# Remove the error console
	if (self._error_console):
		panel = self.window.get_bottom_panel()
		panel.remove_item(self._error_console)
		self._error_console = None
	# Remove the Gtk Widgets
        manager = self.window.get_ui_manager()
        manager.remove_ui(self._ui_merge_id)
        manager.remove_action_group(self._document_actions)
        manager.remove_action_group(self._texsensitive_actions)
        manager.remove_action_group(self._general_actions)
        manager.remove_action_group(self._menu)
        manager.ensure_update()
    
    # Test if a given string is a standard extension for TeX document
    def _is_TeX_extension(self, ext):
	ext = ext.lower()
	if ext == '.tex' or ext =='.latex':
	    return True
	else:
	    return False

    # Replies if the active document is a TeX document
    def _is_TeX_document(self):
        doc = self.window.get_active_document()
        if doc:
            doc = Gedit.Document.get_location(doc)
	    if doc:
		ext = os.path.splitext(doc.get_path())[-1]
		return self._is_TeX_extension(ext)
        return False

    # Try to find the directory where an AutoLaTeX configuration file is
    # located. The search is traversing the parent directory from the current
    # document.
    def _find_AutoLaTeX_dir(self):
        adir = None
        doc = self.window.get_active_document()
        if doc:
            doc = Gedit.Document.get_location(doc)
	    if doc:
		document_name = doc.get_path()
                curdir = Gio.File.new_for_path(os.getcwd())
                doc = doc.get_parent()
		doc = curdir.resolve_relative_path(doc.get_path())
                doc = doc.get_path()
		document_dir = doc
                cfgFile = os.path.join(doc,".autolatex_project.cfg")
                rootFile = os.path.join('/',".autolatex_project.cfg")
	        while rootFile != cfgFile and not os.path.exists(cfgFile):
		    doc = os.path.dirname(doc)
                    cfgFile = os.path.join(doc,".autolatex_project.cfg")

                if rootFile != cfgFile:
                    adir = os.path.dirname(cfgFile)
		else:
		    ext = os.path.splitext(document_name)[-1]
		    if self._is_TeX_extension(ext):
		        adir = document_dir

	return adir

    def _launch_AutoLaTeX(self, directive, params):
	directory = self._find_AutoLaTeX_dir()
	if directory:
	    GObject.idle_add(self._update_action_validity, False, None)
	    thread = AutoLaTeXExecutionThread(self, directory, directive, params)
	    thread.start()

    def on_clean_action_activate(self, action, data=None):
	self._launch_AutoLaTeX('clean', [ '--noview', DEFAULT_LOG_LEVEL ])

    def on_cleanall_action_activate(self, action, data=None):
	self._launch_AutoLaTeX('cleanall', [ '--noview', DEFAULT_LOG_LEVEL ])

    def on_compile_action_activate(self, action, data=None):
	self._launch_AutoLaTeX('all', [ '--noview', DEFAULT_LOG_LEVEL ])

    def on_generateimage_action_activate(self, action, data=None):
	self._launch_AutoLaTeX('images', [ '--noview', DEFAULT_LOG_LEVEL ])

    def on_view_action_activate(self, action, data=None):
	self._launch_AutoLaTeX('view', [ '--asyncview', DEFAULT_LOG_LEVEL ])

    def on_document_configuration_action_activate(self, action, data=None):
	pass

    def on_user_configuration_action_activate(self, action, data=None):
	pass

