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

AutoLaTeX::GUI::Gtk::GeneralPanel - A GTK panel for general management

=head1 DESCRIPTION

AutoLaTeX::GUI::Gtk::GeneralPanel is a Perl module, which permits to
display a Gtk panel that manages AutoLaTeX options.

=head1 METHOD DESCRIPTIONS

This section contains only the methods in GtkGeneralPanel.pm itself.

=over

=cut

package AutoLaTeX::GUI::Gtk::GeneralPanel;

@ISA = qw( Gtk2::Table AutoLaTeX::GUI::Gtk::WidgetUtil AutoLaTeX::GUI::AbstractGeneralPanel );
@EXPORT = qw();
@EXPORT_OK = qw();

use strict;
use vars qw(@ISA @EXPORT @EXPORT_OK $VERSION);
use Exporter;

use Glib qw(TRUE FALSE);
use Gtk2;
use Gtk2::SimpleList;

use AutoLaTeX::Core::Util;
use AutoLaTeX::Core::Locale;
use AutoLaTeX::GUI::AbstractGeneralPanel;
use AutoLaTeX::GUI::Gtk::WidgetUtil;

#------------------------------------------------------
#
# Global vars
#
#------------------------------------------------------

# Version number
my $VERSION = "8.0" ;

my %GENERATION_TYPES_ORIG = (
	_T('01_Generate PDF document') => 'pdf',
	_T('02_Generate DVI document') => 'dvi',
	_T('03_Generate Postscript document') => 'ps',
	_T('04_Generate PDF document via Postscript') => 'pspdf',
	);
my %GENERATION_TYPES = ();

my %MAKEINDEX_STYLE_TYPES_ORIG = (
	_T('01_Use current configuration file value') => '',
	_T('02_Auto-detect the style inside the project directory') => '@detect',
	_T('03_Use only the default AutoLaTeX style') => '@system',
	_T('04_No style is passed to MakeIndex') => '@none',
	);
my %MAKEINDEX_STYLE_TYPES = ();

#------------------------------------------------------
#
# Functions
#
#------------------------------------------------------

=pod

=item * new(\%$)

Contructor.

Parameters are:

=over 4

=item the configuration extracted from the configuration files.

=item is the name of the subroutine that permits to get the configuration filename

=back

=cut
sub new(\%$) : method {
	my $proto = shift;
	my $class = ref($proto) || $proto;

	my $self = bless( $class->SUPER::new(
						4, #rows
						1, #columns
						FALSE), #non uniform
			$class ) ;

	die("The first parameter of AutoLaTeX::GUI::Gtk::GeneralPanel::new() should be a hastable\nIf you pass a %v variable, please use the \%v syntax instead.\n")
		unless ((!defined($_[0]))||(isHash($_[0])));
	$self->attr('configuration') = {};
	%{$self->attr('configuration')} = %{$_[0]};

	$self->attr('configuration-filename') = $_[1];

	# Initialization
	$self->initializeGeneralPanel();

	return $self;
}

=pod

=item * initControls()

Initializing the controls.

=cut
sub initControls() : method {
	my $self = shift;

	# GENERATION part
	{
		my $generationFrame = Gtk2::Frame->new($self->localeGet(_T("Generation")));
		$self->attach ($generationFrame, 
					0,1,0,1, # left, right, top and bottom columns
					['expand','fill'],['expand','fill'], # x and y options
					5,2); # horizontal and vertical paddings
		my $subtable = Gtk2::Table->new (
						5, #rows
						2, #columns
						FALSE); #non uniform
		$generationFrame->add ($subtable);

		my $label1 = Gtk2::Label->new ($self->localeGet(_T("Main TeX file (optional):")));
		$subtable->attach ($label1, 
					0,1,0,1, # left, right, top and bottom columns
					'shrink','shrink', # x and y options
					2,2); # horizontal and vertical paddings

		my $edit1 = Gtk2::Entry->new ();
		$self->connectSignal($edit1,'changed','onMainTeXFileChanged');
		$subtable->attach ($edit1, 
					1,2,0,1, # left, right, top and bottom columns
					['expand','fill'],['expand','fill'], # x and y options
					2,2); # horizontal and vertical paddings
		$self->attr('EDITORS','MAIN_TEX_FILE') = $edit1;

		my $label2b = Gtk2::CheckButton->new ($self->localeGet(_T("Run bibliography tool")));
		$self->connectSignal($label2b,'toggled','onRunBiblioToggled');
		$subtable->attach ($label2b, 
					0,2,1,2, # left, right, top and bottom columns
					['expand','fill'],['expand','fill'], # x and y options
					2,2); # horizontal and vertical paddings
		$self->attr('EDITORS','ENABLE_BIBLIO') = $label2b;

		my $label2 = Gtk2::CheckButton->new ($self->localeGet(_T("Automatic generation of pictures")));
		$self->connectSignal($label2,'toggled','onGenerateImageToggled');
		$subtable->attach ($label2, 
					0,2,2,3, # left, right, top and bottom columns
					['expand','fill'],['expand','fill'], # x and y options
					2,2); # horizontal and vertical paddings
		$self->attr('EDITORS','AUTO_PICTURE_GENERATION') = $label2;


		my $label3 = Gtk2::Label->new ($self->localeGet(_T("Image search directory:")));
		$subtable->attach ($label3, 
					0,1,3,4, # left, right, top and bottom columns
					'shrink','shrink', # x and y options
					2,2); # horizontal and vertical paddings

		my $edit2 = Gtk2::Entry->new ();
		$self->connectSignal($edit2,'changed','onImageSearchDirectoryChanged');
		$subtable->attach ($edit2, 
					1,2,3,4, # left, right, top and bottom columns
					['expand','fill'],['expand','fill'], # x and y options
					2,2); # horizontal and vertical paddings
		$self->attr('EDITORS','AUTO_GENERATE_IMAGE_DIRECTORY') = $edit2;

		my $label4 = Gtk2::Label->new ($self->localeGet(_T("Type of generation:")));
		$subtable->attach ($label4, 
					0,1,4,5, # left, right, top and bottom columns
					'shrink','shrink', # x and y options
					2,2); # horizontal and vertical paddings

		my $edit3 = Gtk2::ComboBox->new_text ();
		$self->fillComboBox('generationType',$edit3,\%GENERATION_TYPES);
		$self->connectSignal($edit3,'changed','onGenerationTypeChanged');
		$subtable->attach ($edit3, 
					1,2,4,5, # left, right, top and bottom columns
					['expand','fill'],'shrink', # x and y options
					2,2); # horizontal and vertical paddings
		$self->attr('EDITORS','GENERATION_TYPE') = $edit3;

		my $label5 = Gtk2::Label->new ($self->localeGet(_T("Type of MakeIndex style research:")));
		$subtable->attach ($label5, 
					0,1,5,6, # left, right, top and bottom columns
					'shrink','shrink', # x and y options
					2,2); # horizontal and vertical paddings

		my $edit4 = Gtk2::ComboBox->new_text ();
		$self->fillComboBox('makeindexStyleType',$edit4,\%MAKEINDEX_STYLE_TYPES);
		$self->connectSignal($edit4,'changed','onMakeIndexStyleChanged');
		$subtable->attach ($edit4, 
					1,2,5,6, # left, right, top and bottom columns
					['expand','fill'],'shrink', # x and y options
					2,2); # horizontal and vertical paddings
		$self->attr('EDITORS','MAKEINDEX_STYLE') = $edit4;
	}

	# VIEWER part
	{
		my $viewerFrame = Gtk2::Frame->new($self->localeGet(_T("Viewer")));
		$self->attach ($viewerFrame, 
					0,1,1,2, # left, right, top and bottom columns
					['expand','fill'],['expand','fill'], # x and y options
					5,2); # horizontal and vertical paddings
		my $subtable = Gtk2::Table->new (
						2, #rows
						2, #columns
						FALSE); #non uniform
		$viewerFrame->add ($subtable);

		my $label1 = Gtk2::CheckButton->new ($self->localeGet(_T("Launch a viewer after compilation")));
		$self->connectSignal($label1,'toggled','onLaunchViewerToggled');
		$subtable->attach ($label1, 
					0,2,0,1, # left, right, top and bottom columns
					['expand','fill'],['expand','fill'], # x and y options
					2,2); # horizontal and vertical paddings
		$self->attr('EDITORS','LAUNCH_VIEWER') = $label1;

		my $label2 = Gtk2::Label->new ($self->localeGet(_T("Command of the viewer (optional):")));
		$subtable->attach ($label2, 
					0,1,1,2, # left, right, top and bottom columns
					'shrink','shrink', # x and y options
					2,2); # horizontal and vertical paddings
		$self->attr('LABELS','VIEWER_PATH') = $label2;

		my $edit1 = Gtk2::Entry->new ();
		$self->connectSignal($edit1,'changed','onPDFViewerChanged');
		$subtable->attach ($edit1, 
					1,2,1,2, # left, right, top and bottom columns
					['expand','fill'],['expand','fill'], # x and y options
					2,2); # horizontal and vertical paddings
		$self->attr('EDITORS','VIEWER_PATH') = $edit1;
	}

	# CLEAN part
	{
		my $cleaningFrame = Gtk2::Frame->new($self->localeGet(_T("Cleaning")));
		$self->attach ($cleaningFrame, 
					0,1,2,3, # left, right, top and bottom columns
					['expand','fill'],['expand','fill'], # x and y options
					5,2); # horizontal and vertical paddings
		my $subtable = Gtk2::Table->new (
						2, #rows
						2, #columns
						FALSE); #non uniform
		$cleaningFrame->add ($subtable);

		my $label1 = Gtk2::Label->new ($self->localeGet(_T("Files to clean:")));
		$subtable->attach ($label1, 
					0,1,0,1, # left, right, top and bottom columns
					'shrink','shrink', # x and y options
					2,2); # horizontal and vertical paddings

		my $edit1 = Gtk2::Entry->new ();
		$self->connectSignal($edit1,'changed','onFilesToCleanChanged');
		$subtable->attach ($edit1, 
					1,2,0,1, # left, right, top and bottom columns
					['expand','fill'],['expand','fill'], # x and y options
					2,2); # horizontal and vertical paddings
		$self->attr('EDITORS','FILES_TO_CLEAN') = $edit1;

		my $label2 = Gtk2::Label->new ($self->localeGet(_T("Files to desintegrate:")));
		$subtable->attach ($label2, 
					0,1,1,2, # left, right, top and bottom columns
					'shrink','shrink', # x and y options
					2,2); # horizontal and vertical paddings

		my $edit2 = Gtk2::Entry->new ();
		$self->connectSignal($edit2,'changed','onFilesToDesintegrateChanged');
		$subtable->attach ($edit2, 
					1,2,1,2, # left, right, top and bottom columns
					['expand','fill'],['expand','fill'], # x and y options
					2,2); # horizontal and vertical paddings
		$self->attr('EDITORS','FILES_TO_DESINTEGRATE') = $edit2;
	}

	# SCM part
	{
		my $scmFrame = Gtk2::Frame->new($self->localeGet(_T("SCM support")));
		$self->attach ($scmFrame, 
					0,1,3,4, # left, right, top and bottom columns
					['expand','fill'],['expand','fill'], # x and y options
					5,2); # horizontal and vertical paddings
		my $subtable = Gtk2::Table->new (
						2, #rows
						2, #columns
						FALSE); #non uniform
		$scmFrame->add ($subtable);

		my $label1 = Gtk2::Label->new ($self->localeGet(_T("Update command line:")));
		$subtable->attach ($label1, 
					0,1,0,1, # left, right, top and bottom columns
					'shrink','shrink', # x and y options
					2,2); # horizontal and vertical paddings

		my $edit1 = Gtk2::Entry->new ();
		$self->connectSignal($edit1,'changed','onSCMUpdateChanged');
		$subtable->attach ($edit1, 
					1,2,0,1, # left, right, top and bottom columns
					['expand','fill'],['expand','fill'], # x and y options
					2,2); # horizontal and vertical paddings
		$self->attr('EDITORS','SCM_UPDATE') = $edit1;

		my $label2 = Gtk2::Label->new ($self->localeGet(_T("Commit command line:")));
		$subtable->attach ($label2, 
					0,1,1,2, # left, right, top and bottom columns
					'shrink','shrink', # x and y options
					2,2); # horizontal and vertical paddings

		my $edit2 = Gtk2::Entry->new ();
		$self->connectSignal($edit2,'changed','onSCMCommitChanged');
		$subtable->attach ($edit2, 
					1,2,1,2, # left, right, top and bottom columns
					['expand','fill'],['expand','fill'], # x and y options
					2,2); # horizontal and vertical paddings
		$self->attr('EDITORS','SCM_COMMIT') = $edit2;
	}
}

=pod

=item * initializeGeneralPanel()

Initializing the panel content before displaying.

=cut
sub initializeGeneralPanel() : method {
	my $self = shift;
	$self->SUPER::initializeGeneralPanel();

	$self->initLocale('autolatexgtk');

	unless (%GENERATION_TYPES) {
		while (my ($k,$v) = each(%GENERATION_TYPES_ORIG)) {
			if ($k =~ /^([0-9]+_)(.*)$/) {
				$k = "$1".$self->localeGet("$2");
			}
			else {
				$k = $self->localeGet("$k");
			}
			$GENERATION_TYPES{"$k"} = $v;
		}
	}

	unless (%MAKEINDEX_STYLE_TYPES) {
		while (my ($k,$v) = each(%MAKEINDEX_STYLE_TYPES_ORIG)) {
			if ($k =~ /^([0-9]+_)(.*)$/) {
				$k = "$1".$self->localeGet("$2");
			}
			else {
				$k = $self->localeGet("$k");
			}
			$MAKEINDEX_STYLE_TYPES{"$k"} = $v;
		}
	}

	$self->initControls();

	# Fill fields
	$self->attr('EDITORS','MAIN_TEX_FILE')->set_text ($self->attr('configuration','generation.main file'))
		if ($self->hasattr('configuration','generation.main file'));
	if ($self->hasattr('configuration','generation.generate images')) {
		$self->attr('EDITORS','AUTO_PICTURE_GENERATION')->set_active ($self->cfgGtkBoolean($self->attr('configuration','generation.generate images')));
	}
	else {
		$self->attr('EDITORS','AUTO_PICTURE_GENERATION')->set_active (TRUE);
	}
	if ($self->hasattr('configuration','generation.biblio')) {
		$self->attr('EDITORS','ENABLE_BIBLIO')->set_active ($self->cfgGtkBoolean($self->attr('configuration','generation.biblio')));
	}
	else {
		$self->attr('EDITORS','ENABLE_BIBLIO')->set_active (TRUE);
	}
	if ($self->hasattr('configuration','generation.image directory')) {
		$self->attr('EDITORS','AUTO_GENERATE_IMAGE_DIRECTORY')->set_text ($self->attr('configuration','generation.image directory'));
	}
	else {
		$self->attr('EDITORS','AUTO_GENERATE_IMAGE_DIRECTORY')->set_text ('.');
	}
	if ($self->hasattr('configuration','generation.generation type')) {
		my $val = $self->attr('configuration','generation.generation type') || '';
		if ($val eq 'pspdf') {
			$self->attr('EDITORS','GENERATION_TYPE')->set_active (3);
		}
		elsif ($val eq 'ps') {
			$self->attr('EDITORS','GENERATION_TYPE')->set_active (2);
		}
		elsif ($val eq 'dvi') {
			$self->attr('EDITORS','GENERATION_TYPE')->set_active (1);
		}
		else {
			$self->attr('EDITORS','GENERATION_TYPE')->set_active (0);
		}
	}
	else {
		$self->attr('EDITORS','GENERATION_TYPE')->set_active (0);
	}
	if ($self->hasattr('configuration','generation.makeindex style')) {
		my $val = $self->attr('configuration','generation.makeindex style') || '';
		if (isArray($val)) {
			if (@{$val} == 1) {
				$val = $val->[0];
			}
			else {
				$val = '';
			}
		}
		if ($val eq '@none') {
			$self->attr('EDITORS','MAKEINDEX_STYLE')->set_active (3);
		}
		elsif ($val eq '@system') {
			$self->attr('EDITORS','MAKEINDEX_STYLE')->set_active (2);
		}
		elsif ($val eq '@detect') {
			$self->attr('EDITORS','MAKEINDEX_STYLE')->set_active (1);
		}
		else {
			$self->attr('EDITORS','MAKEINDEX_STYLE')->set_active (0);
		}		
	}
	else {
		$self->attr('EDITORS','MAKEINDEX_STYLE')->set_active (0);
	}
	if ($self->hasattr('configuration','viewer.view')) {
		$self->attr('EDITORS','LAUNCH_VIEWER')->set_active ($self->cfgGtkBoolean($self->attr('configuration','viewer.view')));
	}
	else {
		$self->attr('EDITORS','LAUNCH_VIEWER')->set_active (TRUE);
	}
	$self->attr('EDITORS','VIEWER_PATH')->set_text ($self->attr('configuration','viewer.viewer'))
		if ($self->hasattr('configuration','viewer.viewer'));
	$self->attr('EDITORS','FILES_TO_CLEAN')->set_text ($self->attr('configuration','clean.files to clean'))
		if ($self->hasattr('configuration','clean.files to clean'));
	$self->attr('EDITORS','FILES_TO_DESINTEGRATE')->set_text ($self->attr('configuration','clean.files to desintegrate'))
		if ($self->hasattr('configuration','clean.files to desintegrate'));
	$self->attr('EDITORS','SCM_UPDATE')->set_text ($self->attr('configuration','scm.scm update'))
		if ($self->hasattr('configuration','scm.scm update'));
	$self->attr('EDITORS','SCM_COMMIT')->set_text ($self->attr('configuration','scm.scm commit'))
		if ($self->hasattr('configuration','scm.scm commit'));
}

#
#------------------------------------- SIGNALS
#

sub onLaunchViewerToggled(@) {
	my $self = shift;

	$self->attr('configuration','viewer.view') = $self->cfgToGtkBoolean($_[0]->get_active ());

	$self->attr('LABELS','VIEWER_PATH')->set_sensitive ($_[0]->get_active ());
	$self->attr('EDITORS','VIEWER_PATH')->set_sensitive ($_[0]->get_active ());
}

sub onGenerateImageToggled(@) {
	my $self = shift;
	$self->attr('configuration','generation.generate images') = $self->cfgToGtkBoolean($_[0]->get_active ());
}

sub onRunBiblioToggled(@) {
	my $self = shift;
	$self->attr('configuration','generation.biblio') = $self->cfgToGtkBoolean($_[0]->get_active ());
}

sub onMainTeXFileChanged(@) {
	my $self = shift;
	$self->attr('configuration','generation.main file') = $_[0]->get_text ();
}

sub onImageSearchDirectoryChanged(@) {
	my $self = shift;
	$self->attr('configuration','generation.image directory') = $_[0]->get_text ();
}

sub onPDFViewerChanged(@) {
	my $self = shift;
	$self->attr('configuration','viewer.viewer') = $_[0]->get_text ();
}

sub onFilesToCleanChanged(@) {
	my $self = shift;
	$self->attr('configuration','clean.files to clean') = $_[0]->get_text ();
}

sub onFilesToDesintegrateChanged(@) {
	my $self = shift;
	$self->attr('configuration','clean.files to desintegrate') = $_[0]->get_text ();
}

sub onSCMUpdateChanged(@) {
	my $self = shift;
	$self->attr('configuration','scm.scm update') = $_[0]->get_text ();
}

sub onSCMCommitChanged(@) {
	my $self = shift;
	$self->attr('configuration','scm.scm commit') = $_[0]->get_text ();
}

sub onGenerationTypeChanged(@) {
	my $self = shift;
	my $value = $self->getComboBoxValue($_[0]);
	$self->attr('configuration','generation.generation type') = $value || 'pdf';
}

sub onMakeIndexStyleChanged(@) {
	my $self = shift;
	my $value = $self->getComboBoxValue($_[0]);
	if ($value) {
		$self->attr('configuration','generation.makeindex style') = $value;
	}
	else {
		$self->deleteattr('configuration','generation.makeindex style');
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
