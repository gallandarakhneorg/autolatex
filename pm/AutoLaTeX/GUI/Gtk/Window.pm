# Copyright (C) 2007-13  Stephane Galland <galland@arakhne.org>
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

=pod

=head1 NAME

AutoLaTeX::GUI::Gtk::Window - A GTK user interface

=head1 DESCRIPTION

AutoLaTeX::GUI::Gtk::Window is a Perl module, which permits to
display a Gtk user interface for AutoLaTeX.

=head1 SYNOPSYS

AutoLaTeX::GUI::Gtk->new() ;

=head1 METHOD DESCRIPTIONS

This section contains only the methods in Gtk.pm itself.

=over

=cut

package AutoLaTeX::GUI::Gtk::Window;

our @ISA = qw( AutoLaTeX::GUI::Gtk::WidgetUtil AutoLaTeX::GUI::AbstractGUI Gtk2::Window );
our @EXPORT = qw();
our @EXPORT_OK = qw();

use strict;
use vars qw(@ISA @EXPORT @EXPORT_OK $VERSION);
use Exporter;

use Glib qw(TRUE FALSE);
use Gtk2 qw/-init -threads-init/;

use AutoLaTeX::Core::Util;
use AutoLaTeX::GUI::AbstractGUI;
use AutoLaTeX::GUI::Gtk::WidgetUtil;
use AutoLaTeX::GUI::Gtk::ToolPanel;
use AutoLaTeX::GUI::Gtk::GeneralPanel;
use AutoLaTeX::GUI::Gtk::TranslatorPanel;

#------------------------------------------------------
#
# Global vars
#
#------------------------------------------------------

# Version number
my $VERSION = "5.3" ;

#------------------------------------------------------
#
# Functions
#
#------------------------------------------------------

=pod

=item * new(\%\%\%\%)

Contructor.

Parameters are:

=over 4

=item the current configuration extracted from the configuration files.

=item the system configuration extracted from the configuration file.

=item the user configuration extracted from the configuration file.

=item the project configuration extracted from the configuration file.

=back

=cut
sub new(\%\%\%\%) : method {
	my $proto = shift;
	my $class = ref($proto) || $proto;

	my $self = bless($class->SUPER::new('toplevel'), $class) ;

	die("The first parameter of AutoLaTeX::GUI::Gtk::Window::new() should be a hastable\nIf you pass a %v variable, please use the \%v syntax instead.\n")
		unless ((!defined($_[0]))||(isHash($_[0])));
	$self->attr('CONFIGURATIONS','FULL') = $_[0];

	die("The second parameter of AutoLaTeX::GUI::Gtk::Window::new() should be a hastable\nIf you pass a %v variable, please use the \%v syntax instead.\n")
		unless ((!defined($_[1]))||(isHash($_[1])));
	$self->attr('CONFIGURATIONS','SYSTEM') = $_[1];

	die("The third parameter of AutoLaTeX::GUI::Gtk::Window::new() should be a hastable\nIf you pass a %v variable, please use the \%v syntax instead.\n")
		unless ((!defined($_[2]))||(isHash($_[2])));
	$self->attr('CONFIGURATIONS','USER') = $_[2];

	die("The forth parameter of AutoLaTeX::GUI::Gtk::Window::new() should be a hastable\nIf you pass a %v variable, please use the \%v syntax instead.\n")
		unless ((!defined($_[3]))||(isHash($_[3])));
	$self->attr('CONFIGURATIONS','PROJECT') = $_[3];

	# Set the windows attributes
	$self->set_title (locGet(_T("AutoLaTeX {}"),getAutoLaTeXVersion()));
	$self->connectSignal($self,'delete-event','onQuit');

	return $self;
}

=pod

=item * setAdminUser($)

Set if the current user is an administrator.

=cut
sub setAdminUser($) : method {
	my $self = shift;
	$self->SUPER::setAdminUser($_[0]);
	my $title = $self->get_title ();
	if ($title =~ /^(.*?)\s*\*ADMINISTRATOR\*\s*$/) {
		$title = "$1";
	}
	if ($_[0]) {
		$title .= " ".$self->localeGet("*ADMINISTRATOR*");
	}
	$self->set_title ("$title");
}

=pod

=item * makeNotebookTab($$)

Replies the GTK component that could be used a a label inside notebook tabs.

=over 4

=item the label of the tab

=item the icon of the tab

=back

=cut
sub makeNotebookTab($$) : method {
	my $self = shift;
	my $tabname = shift;

	my $hbox = Gtk2::HBox->new (FALSE,2);

	my $iconwgt;

	if (@_>1) {
		my $icon = $self->getIcon (shift);
		my $animation = Gtk2::Gdk::PixbufSimpleAnim->new (
					$icon->get_width (),
					$icon->get_height (),
					1); # Rate in fps
		$animation->add_frame ($icon);
		foreach my $iconName (@_) {
			$icon = $self->getIcon ($iconName);
			$animation->add_frame ($icon);
		}
		$iconwgt = Gtk2::Image->new_from_animation ($animation);
	}
	else {
		$iconwgt = Gtk2::Image->new_from_pixbuf ($self->getIcon ($_[0]));
	}

	$hbox->add ($iconwgt);

	my $labelwgt = Gtk2::Label->new ($tabname);
	$hbox->add ($labelwgt);
	$hbox->show_all ();

	return $hbox;
}

=pod

=item * savePanelContents()

Save the content of the panels.

=cut
sub savePanelContents() : method {
	my $self = shift;
	my $tab;
	my @panels = (
			'translatorConfiguration',
			'systemConfiguration',
			'userConfiguration',
			'projectConfiguration',
			'toolPanel',
	);
	foreach my $k (@panels) {
		$tab = $self->attr('NOTEBOOK_PANEL',"$k");
		if (($tab)&&($tab->can('savePanelContent'))) {
			$tab->savePanelContent()
		}
	}
}

=pod

=item * initializeDialogContent()

Initializing the dialog content before displaying.

=cut
sub initializeDialogContent() : method {
	my $self = shift;

	$self->SUPER::initializeDialogContent();

	$self->initLocale('autolatexgtk');

	# Main layout
	my $mainLayout = Gtk2::Table->new (
						2, #rows
						1, #columns
						FALSE); #non uniform
	$self->add ($mainLayout);
	
	# Initialize the panel notebook
	my $notebook = Gtk2::Notebook->new ();
	$self->attr('NOTEBOOK') = $notebook;
	$mainLayout->attach ($notebook, 
				0,1,0,1, # left, right, top and bottom columns
				['fill','expand'],['fill','expand'], # x and y options
				5,5); # horizontal and vertical paddings
	$self->connectSignal($notebook,'switch-page','onNotebookPageChanged');	

	# Close button
	my $buttonAlignment = Gtk2::HButtonBox->new ();
	$buttonAlignment->set_layout('end');

	my $closeButton = Gtk2::Button->new_from_stock ('gtk-close');
	$self->connectSignal($closeButton,'clicked','onQuit');
	$buttonAlignment->add ($closeButton);

	$mainLayout->attach ($buttonAlignment, 
				0,1,1,2, # left, right, top and bottom columns
				['fill','expand'],'shrink', # x and y options
				5,5); # horizontal and vertical paddings

	# Open the tool panel
	my $toolTab = AutoLaTeX::GUI::Gtk::ToolPanel->new ($self->attr('CONFIGURATIONS','FULL'));
	$toolTab->setAdminUser( $self->isAdminUser() );
	$self->attr('NOTEBOOK_PANEL','toolPanel') = $toolTab;
	$notebook->append_page($toolTab, $self->makeNotebookTab(
				$self->localeGet(_T("Tools")), "tools.png"));

	# Open the project configuration
	if ($self->hasProject ()) {
		my $projectConfTab = AutoLaTeX::GUI::Gtk::GeneralPanel->new (
					$self->attr('CONFIGURATIONS','PROJECT'),
					'getProjectConfigFilename');
		$projectConfTab->setAdminUser( $self->isAdminUser() );
		$self->attr('NOTEBOOK_PANEL','projectConfiguration') = $projectConfTab;
		$notebook->append_page($projectConfTab, $self->makeNotebookTab(
				$self->localeGet(_T("Project Configuration")), "projectLevel.png"));
	}

	# Create the user configuration panel
	my $userConfTab = AutoLaTeX::GUI::Gtk::GeneralPanel->new (
					$self->attr('CONFIGURATIONS','USER'),
					'getUserConfigFilename');
	$userConfTab->setAdminUser( $self->isAdminUser() );
	$self->attr('NOTEBOOK_PANEL','userConfiguration') = $userConfTab;
	$notebook->append_page($userConfTab, $self->makeNotebookTab(
				$self->localeGet(_T("User Configuration")), "userLevel.png"));

	# Open the system configuration only if root
	if ($self->isAdminUser ()) {
		my $systemConfTab = AutoLaTeX::GUI::Gtk::GeneralPanel->new (
						$self->attr('CONFIGURATIONS','SYSTEM'),
						'getSystemConfigFilename');
		$systemConfTab->setAdminUser( $self->isAdminUser() );
		$self->attr('NOTEBOOK_PANEL','systemConfiguration') = $systemConfTab;
		$notebook->append_page($systemConfTab, $self->makeNotebookTab(
				$self->localeGet(_T("System Configuration")), "systemLevel.png"));
	}

	# Create the translator panel
	my $translatorTab = AutoLaTeX::GUI::Gtk::TranslatorPanel->new (
				$self->attr('CONFIGURATIONS','FULL'),
				$self->attr('CONFIGURATIONS','SYSTEM'),
				$self->attr('CONFIGURATIONS','USER'),
				$self->attr('CONFIGURATIONS','PROJECT'),
				$self);
	$translatorTab->setAdminUser( $self->isAdminUser() );
	$self->attr('NOTEBOOK_PANEL','translatorConfiguration') = $translatorTab;

}

=pod

=item * doLoop()

Do the GUI interaction loop. It means that the dialog
must be displayed now and ready for interaction.

=cut
sub doLoop() : method {
	my $self = shift;
	$self->show_all;
	my $quit = FALSE;
	my $lastmsg = '';
	resetQuitGtkFlag();
	while (!mustQuitGtk()) {
		while (Gtk2->events_pending()) {
			Gtk2->main_iteration();
		}
		notifySystemCommandListeners();
	}

}

=pod

=item * destroyDialogContent()

Destroying the dialog content after the application was quitted.

=cut
sub destroyDialogContent() : method {
	my $self = shift;

	$self->savePanelContents();

	$self->SUPER::destroyDialogContent();
}

=pod

=item * onTranslatorPanelStateChanged($$)

Invoked when the translator panel has its state changed.

=cut
sub onTranslatorPanelStateChanged($$) {
	my $self = shift;
	my $panel = shift;
	my $conflict = shift;

	my $tabTitle;
	if ($conflict) {
		$tabTitle = $self->makeNotebookTab($self->localeGet(_T("Translators")), "translators_err.png", "translators.png", "translators_err.png", "translators.png", "translators_err.png", "translators.png", "translators_err.png");
	}
	else {
		$tabTitle = $self->makeNotebookTab($self->localeGet(_T("Translators")), "translators.png");
	}

	if ($self->hasattr('NOTEBOOK_PANEL','translatorConfiguration')) {
		$self->attr('NOTEBOOK')->set_tab_label (
				$panel,
				$tabTitle);
	}
	else {
		$self->attr('NOTEBOOK')->append_page(
				$panel,
				$tabTitle);
	}
}

=pod

=item * onTranslatorPanelStateChanged($$)

Invoked when the translator panel has its state changed.

=cut
sub onNotebookPageChanged($$) {
	my $self = shift;
	my $notebook = $_[0];
	my $newpagenum = $_[2]|| 0;
	my $oldpagenum = $notebook->get_current_page ();
	if ($oldpagenum>=0) {
		my $pageObj = $notebook->get_nth_page ($oldpagenum);
		if ($pageObj->can('savePanelContent')) {
			printDbgFor(3,locGet(_T("Saving hidden notebook panel")));
			$pageObj->savePanelContent ();
		}
	}
}

1;
__END__

=back

=head1 COPYRIGHT

(c) Copyright 2007-13 Stephane Galland E<lt>galland@arakhne.orgE<gt>, under GPL.

=head1 AUTHORS

=over

=item *

Conceived and initially developed by Stéphane Galland E<lt>galland@arakhne.orgE<gt>.

=back

=head1 SEE ALSO

L<autolatex>
