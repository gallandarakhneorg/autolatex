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

AutoLaTeX::GUI::AbstractGUI - An abstract user interface

=head1 DESCRIPTION

AutoLaTeX::GUI::AbstractGUI is a Perl module, which permits to
display an user interface for AutoLaTeX.

=head1 METHOD DESCRIPTIONS

This section contains only the methods in AbstractGUI.pm itself.

=over

=cut

package AutoLaTeX::GUI::AbstractGUI;

@ISA = ('Exporter');
@EXPORT = qw();
@EXPORT_OK = qw();

require 5.014;
use strict;
use vars qw(@ISA @EXPORT @EXPORT_OK $VERSION);
use Exporter;

use AutoLaTeX::Core::IntUtils;

#------------------------------------------------------
#
# Global vars
#
#------------------------------------------------------

# Version number
my $VERSION = "6.0" ;

=pod

=item * setCommandLine($@)

Specify the command line parameters.

Parameters are:

=over 4

=item the name of the command

=item the list of command line parameters

=back

=cut
sub setCommandLine($@) : method {
	my $self = shift;
	my $command = shift || printErr(_T("Command name not specified"));
	$self->{'ARGV'} = [ @_ ];
	unshift @{$self->{'ARGV'}}, "$command";
	$self->{'ARGV'};
}

=pod

=item * getArgv($)

Replies the i-th command line parameter.

=cut
sub getArgv($) : method {
	my $self = shift;
	my $ith = shift;
	return undef
		unless(
			($ith>=0)&&
			(exists $self->{'ARGV'})&&
			(isArray($self->{'ARGV'}))&&
			($ith<@{$self->{'ARGV'}}));
	return $self->{'ARGV'}["$ith"];
}

=pod

=item * showDialog()

Show the dialog.

=cut
sub showDialog() : method {
	my $self = shift;
	$self->initializeDialogContent();
	$self->doLoop();
	$self->destroyDialogContent();
}

=pod

=item * initializeDialogContent()

Initializing the dialog content before displaying.

This method read the list of the translators and
fill the attribute C<{'DATA'}{'translators'}>.

=cut
sub initializeDialogContent() : method {
	my $self = shift;
}

=pod

=item * doLoop()

Do the GUI interaction loop. It means that the dialog
must be displayed now and ready for interaction.

=cut
sub doLoop() : method {
	die("You must override AbstractGUI::doLoop()\n");
}

=pod

=item * destroyDialogContent()

Destroying the dialog content after the application was quitted.

=cut
sub destroyDialogContent() : method {
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
