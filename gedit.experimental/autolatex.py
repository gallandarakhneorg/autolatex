import os
from gi.repository import GObject, Gtk, Gedit, Gio
from subprocess import call

UI_XML = """<ui>
<menubar name="MenuBar">
    <menu name="ToolsMenu" action="Tools">
      <placeholder name="ToolsOps_3">
	<menu name="AutoLaTeXMenu" action="AutoLaTeXMenu">
	  <menuitem name="AutoLaTeXCleanAction" action="AutoLaTeXCleanAction"/>
	  <menuitem name="AutoLaTeXCompileAction" action="AutoLaTeXCompileAction"/>
	  <menuitem name="AutoLaTeXCleanallAction" action="AutoLaTeXCleanallAction"/>
        </menu>
      </placeholder>
    </menu>
</menubar>
</ui>"""


class AutoLaTeXPlugin(GObject.Object, Gedit.WindowActivatable):
    __gtype_name__ = "AutoLaTeXPlugin"
    window = GObject.property(type=Gedit.Window)
    
    def __init__(self):
        GObject.Object.__init__(self)
    
    def do_activate(self):
        self._add_ui()

    def do_deactivate(self):
        self._remove_ui()

    def do_update_state(self):
        pass



    def _add_ui(self):
        manager = self.window.get_ui_manager()
        self._actions = Gtk.ActionGroup("AutoLaTeXActions")
        self._actions.add_actions([
            ('AutoLaTeXMenu', None, "AutoLaTeX", 
                None, "AutoLaTeX", 
                None),
            ('AutoLaTeXCleanAction', None, "Remove temporary files", 
                None, "Clean with AutoLaTeX", 
                self.on_clean_action_activate),
            ('AutoLaTeXCompileAction', Gtk.STOCK_EXECUTE, "Compile", 
                '<shift><ctrl>R', "Compile with AutoLaTeX", 
                self.on_compile_action_activate),
            ('AutoLaTeXCleanallAction', None, "Clean all", 
                '<shift><ctrl>C', "Clean all with AutoLaTeX", 
                self.on_cleanall_action_activate),
        ])
        manager.insert_action_group(self._actions)
        self._ui_merge_id = manager.add_ui_from_string(UI_XML)
        manager.ensure_update()
        
    def _remove_ui(self):
        manager = self.window.get_ui_manager()
        manager.remove_ui(self._ui_merge_id)
        manager.remove_action_group(self._actions)
        manager.ensure_update()
    
    def _findAutoLaTeXDir(self):
        adir = None
        doc = self.window.get_active_document()
        if doc:
            doc = Gedit.Document.get_location(doc)
	    if doc:
                curdir = Gio.File.new_for_path(os.getcwd());
                doc = doc.get_parent()
		doc = curdir.resolve_relative_path(doc.get_path())
                doc = doc.get_path()
                cfgFile = os.path.join(doc,".autolatex_project.cfg")
                rootFile = os.path.join('/',".autolatex_project.cfg")
	        while rootFile != cfgFile and not os.path.exists(cfgFile):
		    doc = os.path.dirname(doc)
                    cfgFile = os.path.join(doc,".autolatex_project.cfg")

                if rootFile != cfgFile:
                    adir = os.path.dirname(cfgFile)

	return adir

    def on_clean_action_activate(self, action, data=None):
	doc = self._findAutoLaTeXDir()
        if doc:
	    print "AutoLaTeX: clean in '%s'.\n" % doc
	    os.chdir(doc)
            call(["autolatex", "--noview", "clean"])

    def on_cleanall_action_activate(self, action, data=None):
	doc = self._findAutoLaTeXDir()
        if doc:
	    print "AutoLaTeX: clean all in '%s'.\n" % doc
	    os.chdir(doc)
            call(["autolatex", "--noview", "cleanall"])

    def on_compile_action_activate(self, action, data=None):
	doc = self._findAutoLaTeXDir()
        if doc:
	    print "AutoLaTeX: compile in '%s'.\n" % doc
	    os.chdir(doc)
            call(["autolatex", "--noview"])

