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

AutoLaTeX::GUI::Gtk::ToolPanel - A GTK panel for tools

=head1 DESCRIPTION

AutoLaTeX::GUI::Gtk::ToolPanel is a Perl module, which permits to
display a Gtk panel that launchs AutoLaTeX tools.

=head1 METHOD DESCRIPTIONS

This section contains only the methods in ToolPanel.pm itself.

=over

=cut

package AutoLaTeX::GUI::Gtk::ToolPanel;

@ISA = qw( Gtk2::Table AutoLaTeX::GUI::Gtk::WidgetUtil AutoLaTeX::GUI::AbstractToolPanel );
@EXPORT = qw();
@EXPORT_OK = qw();

use strict;
use vars qw(@ISA @EXPORT @EXPORT_OK $VERSION);
use Exporter;

use Glib qw(TRUE FALSE);
use Gtk2;

use File::Basename;

use AutoLaTeX::Core::Util;
use AutoLaTeX::Core::Main;
use AutoLaTeX::Core::Locale;
use AutoLaTeX::GUI::AbstractToolPanel;
use AutoLaTeX::GUI::Gtk::WidgetUtil;

#------------------------------------------------------
#
# Global vars
#
#------------------------------------------------------

# Version number
my $VERSION = "6.0" ;

# Available commands
my @LAUNCH_COMMAND_ORDER = ( 'gnome', 'kde', 'stdout' );
my %LAUNCH_COMMANDS = (
	'gnome' => [ 'gnome-terminal', '-x', 'autolatex' ],
	'kde' => [ 'konsole', '-e', 'autolatex' ],
	'stdout' => [ 'autolatex' ],
	);
my %LAUNCH_COMMAND_LIST_ORIG = (
	_T('01_No prefered launcher, use first available') => 'none',
	_T('02_Gnome terminal') => 'gnome',
	_T('03_KDE console') => 'kde',
	_T('04_No graphical terminal') => 'stdout',
	);
my %LAUNCH_COMMAND_LIST = ();

#------------------------------------------------------
#
# Functions
#
#------------------------------------------------------

=pod

=item * new(\%)

Contructor.

=over 4

=item general configuration

=back

=cut
sub new(\%) : method {
	my $proto = shift;
	my $class = ref($proto) || $proto;

	my $self = bless( $class->SUPER::new(
						3, #rows
						2, #columns
						FALSE), #non uniform
			$class ) ;

	die("The first parameter of AutoLaTeX::GUI::Gtk::GeneralPanel::new() should be a hastable\nIf you pass a %v variable, please use the \%v syntax instead.\n")
		unless ((!defined($_[0]))||(isHash($_[0])));
	$self->attr('CONFIGURATION') = $_[0];

	# Initialization
	$self->initializeToolPanel();

	return $self;
}

=pod

=item * initControls()

Initializing the controls.

=cut
sub initControls() : method {
	my $self = shift;

	# Build components
	my $filenameLabel = Gtk2::Label->new ($self->localeGet(_T("Main TeX file:")));
	$self->attach ($filenameLabel, 
				0,1,0,1, # left, right, top and bottom columns
				'shrink','shrink', # x and y options
				20,20); # horizontal and vertical paddings
	my $filenameLabel2 = Gtk2::Label->new ('');
	$self->attr('CONTROLS','FILENAME') = $filenameLabel2;
	$self->attach ($filenameLabel2, 
				1,2,0,1, # left, right, top and bottom columns
				['fill','expand'],'shrink', # x and y options
				20,20); # horizontal and vertical paddings

	my $preferedUILabel = Gtk2::Label->new ($self->localeGet(_T("Prefered Launcher:")));
	$self->attach ($preferedUILabel, 
				0,1,1,2, # left, right, top and bottom columns
				'shrink','shrink', # x and y options
				20,20); # horizontal and vertical paddings

	my $preferedUI = Gtk2::ComboBox->new_text ();
	$self->fillComboBox('preferedUI',$preferedUI,\%LAUNCH_COMMAND_LIST);
	$self->attr('CONTROLS','PREFERED_UI_COMBO') = $preferedUI;
	$self->connectSignal($preferedUI,'changed','onPreferedUIChanged');
	$self->attach ($preferedUI, 
				1,2,1,2, # left, right, top and bottom columns
				['fill','expand'],'shrink', # x and y options
				20,20); # horizontal and vertical paddings

	my $buttonList = Gtk2::HButtonBox->new ();
	$buttonList->set_layout ('spread');
	$buttonList->set_spacing (5);
	$self->attach ($buttonList, 
				0,2,2,3, # left, right, top and bottom columns
				['fill','expand'],['fill','expand'], # x and y options
				20,20); # horizontal and vertical paddings

	my $compileButton = Gtk2::Button->new_from_stock ('gtk-execute');
	$self->attr('CONTROLS','COMPILE_BUTTON') = $compileButton;
	$self->connectSignal($compileButton,'clicked','onCompileButtonClicked');
	$buttonList->add ($compileButton);	

	my $cleanCompileButton = Gtk2::Button->new_with_label ($self->localeGet(_T("Clean and Execute")));
	$cleanCompileButton->set_image (Gtk2::Image->new_from_stock ('gtk-execute', 'button'));
	$self->attr('CONTROLS','CLEAN_COMPILE_BUTTON') = $cleanCompileButton;
	$self->connectSignal($cleanCompileButton,'clicked','onCleanCompileButtonClicked');
	$buttonList->add ($cleanCompileButton);	

	my $cleanButton = Gtk2::Button->new_with_label ($self->localeGet(_T("Clean")));
	$cleanButton->set_image (Gtk2::Image->new_from_file ($self->getIconPath('clean.png')));
	$self->attr('CONTROLS','CLEAN_BUTTON') = $cleanButton;
	$self->connectSignal($cleanButton,'clicked','onCleanButtonClicked');
	$buttonList->add ($cleanButton);	

	my $cleanallButton = Gtk2::Button->new_with_label ($self->localeGet(_T("Clean all")));
	$cleanallButton->set_image (Gtk2::Image->new_from_file ($self->getIconPath('cleanall.png')));
	$self->attr('CONTROLS','CLEANALL_BUTTON') = $cleanallButton;
	$self->connectSignal($cleanallButton,'clicked','onCleanallButtonClicked');
	$buttonList->add ($cleanallButton);	

	my $refreshButton = Gtk2::Button->new_from_stock ('gtk-refresh');
	$self->connectSignal($refreshButton,'clicked','onRefreshButtonClicked');
	$buttonList->add ($refreshButton);	
}

=pod

=item * initializeToolPanel()

Initializing the panel content before displaying.

=cut
sub initializeToolPanel() : method {
	my $self = shift;
	$self->SUPER::initializeToolPanel();

	$self->initLocale('autolatexgtk');

	unless (%LAUNCH_COMMAND_LIST) {
		while (my ($k,$v) = each(%LAUNCH_COMMAND_LIST_ORIG)) {
			if ($k =~ /^([0-9]+_)(.*)$/) {
				$k = "$1".$self->localeGet("$2");
			}
			else {
				$k = $self->localeGet("$k");
			}
			$LAUNCH_COMMAND_LIST{"$k"} = $v;
		}
	}

	$self->initControls();

	my $preferedUI = $self->attr('CONFIGURATION','gtk.preferred launcher');
	if (($preferedUI)&&(exists $LAUNCH_COMMANDS{"$preferedUI"})) {
		my $combo = $self->attr('CONTROLS','PREFERED_UI_COMBO');
		my $index = $self->getComboBoxValueIndex ($combo, "$preferedUI");
		$index = 0 if ($index<0);
		$self->attr('CONTROLS','PREFERED_UI_COMBO')->set_active ($index);
	}
	else {
		$self->attr('CONTROLS','PREFERED_UI_COMBO')->set_active (0);
	}	

	$self->refresh();
}

=pod

=item * saveGUIConfiguration(\%)

Save the GUI configuration inside the specified configuration.

=over 4

=item is the configuration to fill

=back

=cut
sub saveGUIConfiguration(\%) {
	my $self = shift;
	my $preferedUI = $self->attr('CONFIGURATION','gtk.preferred launcher');
	printDbgFor(4,locGet(_T("Preferred launcher: {}"), $preferedUI));
	$_[0]->{'gtk.preferred launcher'} = $preferedUI;
}

=pod

=item * refresh()

Refreshing the panel.

=cut
sub refresh() : method {
	my $self = shift;
	my $currentConfig = $self->attr('CONFIGURATION');

	my %configuration = ();
	$configuration{'__private__'}{'output.directory'} = $currentConfig->{'__private__'}{'output.directory'};
	detectMainTeXFile(%configuration);

	my $active = FALSE;
	if ($configuration{'__private__'}{'input.latex file'}) {
		$self->attr('CONTROLS','FILENAME')->set_text (basename($configuration{'__private__'}{'input.latex file'}));
		$active = TRUE;
	}
	else {
		$self->attr('CONTROLS','FILENAME')->set_text ('???');
	}
	$self->attr('CONTROLS','COMPILE_BUTTON')->set_sensitive ($active);
	$self->attr('CONTROLS','CLEAN_COMPILE_BUTTON')->set_sensitive ($active);
	$self->attr('CONTROLS','CLEAN_BUTTON')->set_sensitive ($active);
	$self->attr('CONTROLS','CLEANALL_BUTTON')->set_sensitive ($active);
}

=pod

=item * launchAutoLaTeX(@)

Launching AutoLaTeX inside a child process.

=over 4

=item the list of parameters to pass to AutoLaTeX

=back

=cut
sub launchAutoLaTeX(@) : method {
	my $self = shift;

	$self->localeDbg(_T("Launching AutoLaTeX with parameters: {}"),join(' ',@_));
	printDbgIndent();

	$self->attr('CONTROLS','COMPILE_BUTTON')->set_sensitive (FALSE);
	$self->attr('CONTROLS','CLEAN_COMPILE_BUTTON')->set_sensitive (FALSE);
	$self->attr('CONTROLS','CLEAN_BUTTON')->set_sensitive (FALSE);
	$self->attr('CONTROLS','CLEANALL_BUTTON')->set_sensitive (FALSE);

	my $succeed = 0;
	my %LAUNCHERS = %LAUNCH_COMMANDS;

	my $preferedUI = $self->attr('CONFIGURATION','gtk.preferred launcher');
	if (($preferedUI)&&(exists $LAUNCHERS{"$preferedUI"})) {
		$self->localeDbg(_T("trying prefered launcher: {}"), $preferedUI);
		my $command = $LAUNCHERS{"$preferedUI"};
		if (runSystemCommand($self,@{$command}, @_) == 0) {
			$self->localeDbg(_T("launch succeeded"));
			$succeed = 1;
		}
		delete $LAUNCHERS{"$preferedUI"};
	}

	unless ($succeed) {
		foreach my $cmdlabel (@LAUNCH_COMMAND_ORDER) {
			if (exists $LAUNCHERS{"$cmdlabel"}) {
				$self->localeDbg(_T("trying {}"),$cmdlabel);
				my $command = $LAUNCHERS{"$cmdlabel"};
				if (runSystemCommand($self,@{$command}, @_) == 0) {
					$self->localeDbg(_T("launch succeeded"));
					$succeed = 1;
					last;
				}
			}
		}
	}

	printDbgUnindent();
}

#
#------------------------------------- SIGNALS
#

sub onSystemCommandTerminaison(\@$) {
	my $self = shift;
	$self->attr('CONTROLS','COMPILE_BUTTON')->set_sensitive (TRUE);
	$self->attr('CONTROLS','CLEAN_COMPILE_BUTTON')->set_sensitive (TRUE);
	$self->attr('CONTROLS','CLEAN_BUTTON')->set_sensitive (TRUE);
	$self->attr('CONTROLS','CLEANALL_BUTTON')->set_sensitive (TRUE);
}

sub onPreferedUIChanged(@) {
	my $self = shift;
	my $value = $self->getComboBoxValue($self->attr('CONTROLS','PREFERED_UI_COMBO'));
	$self->attr('CONFIGURATION','gtk.preferred launcher') = $value;
}

sub onCompileButtonClicked(@) {
	my $self = shift;
	$self->launchAutoLaTeX ('all');
}

sub onCleanCompileButtonClicked(@) {
	my $self = shift;
	$self->launchAutoLaTeX ('clean', 'all');
}

sub onCleanButtonClicked(@) {
	my $self = shift;
	$self->launchAutoLaTeX ('clean');
}

sub onCleanallButtonClicked(@) {
	my $self = shift;
	$self->launchAutoLaTeX ('cleanall');
}

sub onRefreshButtonClicked(@) {
	my $self = shift;
	$self->refresh ();
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
