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

AutoLaTeX::GUI::Gtk::WidgetUtil - A GTK widget utility class

=head1 DESCRIPTION

AutoLaTeX::GUI::Gtk::WidgetUtil is a Perl module, which provides
utility methods for GtkWidgets.

=head1 METHOD DESCRIPTIONS

This section contains only the methods in WidgetUtil.pm itself.

=over

=cut

package AutoLaTeX::GUI::Gtk::WidgetUtil;

@ISA = qw( AutoLaTeX::GUI::WidgetUtil );
@EXPORT = qw( &resetQuitGtkFlag &quitGtk &mustQuitGtk );
@EXPORT_OK = qw();

use strict;
use vars qw(@ISA @EXPORT @EXPORT_OK $VERSION);
use Exporter;

use Glib qw(TRUE FALSE);
use Gtk2 qw/-init -threads-init/;

use File::Basename;
use File::Spec;
use AutoLaTeX::Core::Util;
use AutoLaTeX::Core::Config;
use AutoLaTeX::GUI::WidgetUtil;

#------------------------------------------------------
#
# Global vars
#
#------------------------------------------------------

# Version number
my $VERSION = "5.1" ;

# Does the GTK Main loop must be quitted
my $QUITGTK = TRUE;

#------------------------------------------------------
#
# Functions
#
#------------------------------------------------------

=pod

=item * getLevelIcon($)

Replies the icon for the specified configuration level.

=cut
sub getLevelIcon($) {
	my $self = shift;
	my $level = shift || '';
	my $iconName;
	if ($level eq 'project') {
		$iconName = 'projectLevel.png';
	}
	elsif ($level eq 'user') {
		$iconName = 'userLevel.png';
	}
	else {
		$iconName = 'systemLevel.png';
	}
	return $self->getIcon($iconName);
}

=pod

=item * getGrayedLevelIcon($)

Replies the grayed icon for the specified configuration level.

=cut
sub getGrayedLevelIcon($) {
	my $self = shift;
	my $level = shift || '';
	my $iconName;
	if ($level eq 'project') {
		$iconName = 'projectLevel_u.png';
	}
	elsif ($level eq 'user') {
		$iconName = 'userLevel_u.png';
	}
	else {
		$iconName = 'systemLevel_u.png';
	}
	return $self->getIcon($iconName);
}

=pod

=item * getRedLevelIcon($)

Replies the red-crossed icon for the specified configuration level.

=cut
sub getRedLevelIcon($) {
	my $self = shift;
	my $level = shift || '';
	my $iconName;
	if ($level eq 'project') {
		$iconName = 'projectLevel_ko.png';
	}
	elsif ($level eq 'user') {
		$iconName = 'userLevel_ko.png';
	}
	else {
		$iconName = 'systemLevel_ko.png';
	}
	return $self->getIcon($iconName);
}

=pod

=item * getConflictLevelIcon($)

Replies the conflict icon for the specified configuration level.

=cut
sub getConflictLevelIcon($) {
	my $self = shift;
	my $level = shift || '';
	my $iconName;
	if ($level eq 'project') {
		$iconName = 'projectLevel_c.png';
	}
	elsif ($level eq 'user') {
		$iconName = 'userLevel_c.png';
	}
	else {
		$iconName = 'systemLevel_c.png';
	}
	return $self->getIcon($iconName);
}

=pod

=item * getGrayedConflictLevelIcon($)

Replies the grayed conflict icon for the specified configuration level.

=cut
sub getGrayedConflictLevelIcon($) {
	my $self = shift;
	my $level = shift || '';
	my $iconName;
	if ($level eq 'project') {
		$iconName = 'projectLevel_uc.png';
	}
	elsif ($level eq 'user') {
		$iconName = 'userLevel_uc.png';
	}
	else {
		$iconName = 'systemLevel_uc.png';
	}
	return $self->getIcon($iconName);
}

=pod

=item * getIconPath($)

Replies the complete path to the specified icon.

=cut
sub getIconPath($) : method {
	my $self = shift;
	my $iconname = shift;
	
	my $filename = File::Spec->catfile(dirname(__FILE__),"$iconname");

	return $filename if (-e "$filename");
	return $self->SUPER::getIconPath($iconname);
}

=pod

=item * getIcon($)

Replies a pixbuf that contains the given icon.

=cut
sub getIcon($) {
	my $self = shift;
	my $iconName = shift;

	if ($self->hasattr('BUFFERS','icons',"$iconName")) {
		return $self->attr('BUFFERS','icons',"$iconName");
	}

	my $iconPath = $self->getIconPath($iconName);
	printErr($self->localeGet(_T("icon not found: {}"), $iconName)) unless ($iconPath);

	my $icon = Gtk2::Gdk::Pixbuf->new_from_file ($iconPath);

	$self->attr('BUFFERS','icons',"$iconName") = $icon;

	return $icon;
}

=pod

=item * connectSignal($$$)

Initializing the dialog content before displaying.

=over 4

=item the Gtk object to connect to the signal

=item the name of the signal to connect

=item the name of the subroutine to call when the signal was triggered.

=back

=cut

sub connectSignal($$$) : method {
	my $self = shift;
	my $obj = shift;
	my $signame = shift;
	my $procname = shift;

	my $proc = sub {
		my $refself = $self;
		my $refprocname = $procname;
		my $refobj = $obj;
		if ($refself->isAllowedSignal($refprocname,$refobj)) {
			$self->localeDbg(_T("{}: on Gtk signal '{}', calling {}(\$)"),scalar(localtime),$signame,$procname);
			eval("\$refself->$procname(\@_);");
			if ($@) {
				printDbg(locGet(_T("{}(\$):"),$procname),$@);
			}		
		}
		else {
			$self->localeDbg(_T("Ignoring Gtk signal '{}'"),$signame);
		}
	};

	$obj->signal_connect ( $signame => $proc );
	return 1;
}

=pod

=item * ignoreSignal($@)

Ignore the given signal.

=over 4

=item the name of the signal handler subroutine.

=item a list of source objects from which the signal must be ignore. If not specified, all source objects match.

=back

=cut

sub ignoreSignal($@) : method {
	my $self = shift;
	my $signame = shift;
	my @sources = (@_);
	$self->{'AUTOLATEX_IGNORED_SIGNALS'}{"$signame"} = \@sources;
	return 1;
}

=pod

=item * allowSignal($)

Allow the given signal.

=over 4

=item the name of the signal handler subroutine.

=back

=cut

sub allowSignal($) : method {
	my $self = shift;
	my $signame = shift;
	delete $self->{'AUTOLATEX_IGNORED_SIGNALS'}{"$signame"};
	return 1;
}

=pod

=item * isAllowedSignal($$)

Replies if the given signal for the specified source must be ignored.

=over 4

=item the name of the signal handler subroutine.

=item the signal source.

=back

=cut

sub isAllowedSignal($$) : method {
	my $self = shift;
	my $signame = shift;
	my $source = shift;
	if (exists $self->{'AUTOLATEX_IGNORED_SIGNALS'}{"$signame"}) {
		return FALSE unless (@{$self->{'AUTOLATEX_IGNORED_SIGNALS'}{"$signame"}});
		foreach my $src (@{$self->{'AUTOLATEX_IGNORED_SIGNALS'}{"$signame"}}) {
			return FALSE if ($src == $source);
		}
	}
	return TRUE;
}

=pod

=item * cfgGtkBoolean($;$)

Replies the GTK value that corresponds to the specified boolean attribute field.

=over 4

=item the name of the configuration field.

=item the data structure to fill.

=back

=cut
sub cfgGtkBoolean($;$) : method {
	my $self = shift;
	return (cfgBoolean($_[0],$_[1])) ? TRUE : FALSE;
}

=pod

=item * cfgToGtkBoolean($)

Replies the configuration value that corresponds to the specified boolean GTK boolean.

=over 4

=item the GTK boolean.

=back

=cut
sub cfgToGtkBoolean($) : method {
	my $self = shift;
	return cfgToBoolean($_[0]);
}

=pod

=item * fillComboBox($$\%)

Fill the combo box with the specified set of values.

The value labels must be prefixed by the order index

=over 4

=item is the identifier of the combo.

=item the GTKComboBox.

=item the hashtable containing the labels and the associated values.

=back

=cut
sub fillComboBox($$\%) : method {
	my $self = shift;
	my $id = shift;
	my $combobox = shift;
	my $values = shift;
	my @humanValues = sort keys %{$values};
	$self->attr('CONSTANTS','COMBOBOXES',"$id") = [];
	$combobox->set_name ($id);
	foreach my $k (@humanValues) {
		if ($k =~ /^([0-9]+)_(.*)$/) {
			my ($level,$label) = ("$1","$2");
			$combobox->append_text ($label);
			$self->attr('CONSTANTS','COMBOBOXES',"$id")->[$level-1] = $values->{"$k"};
		}
	}
	return 1;
}

=pod

=item * getComboBoxValue($)

Replies the values selected by the specified combo box.

=over 4

=item the GTKComboBox.

=back

=cut
sub getComboBoxValue($) : method {
	my $self = shift;
	my $combobox = shift;
	my $id = $combobox->get_name ();
	if ($self->hasattr('CONSTANTS','COMBOBOXES',"$id")) {
		my $values = $self->attr('CONSTANTS','COMBOBOXES',"$id");
		my $index = $combobox->get_active ();
		if (($index>=0)&&($index<@{$values})) {
			return $values->[$index];
		}
	}
	return undef;
}

=pod

=item * getComboBoxValueIndex($$)

Replies the index of the specified value in a combo box, or -1 on error.

=over 4

=item the GTKComboBox.

=item the desired value.

=back

=cut
sub getComboBoxValueIndex($$) : method {
	my $self = shift;
	my $combobox = shift;
	my $desiredValue = shift;
	my $id = $combobox->get_name ();
	if ($self->hasattr('CONSTANTS','COMBOBOXES',"$id")) {
		my $values = $self->attr('CONSTANTS','COMBOBOXES',"$id");
		return arrayIndexOf (@{$values}, "$desiredValue");
	}
	return -1;
}

=pod

=item * quitGtk()

Quit the Gtk main loop.

=cut
sub quitGtk() {
	$QUITGTK = TRUE;
}

=pod

=item * mustQuitGtk()

Indicates of Quit the Gtk main loop.

=cut
sub mustQuitGtk() {
	return $QUITGTK;
}

=pod

=item * resetQuitGtkFlag()

Reset the flag that indicates if the Gtk main loop must be quitted.

=cut
sub resetQuitGtkFlag() {
	$QUITGTK = FALSE;
}


#
#------------------------------------- SIGNALS
#

sub onQuit(@) : method {
	quitGtk();
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
