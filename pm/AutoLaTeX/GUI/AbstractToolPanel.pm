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

AutoLaTeX::GUI::AbstractToolPanel - An abstract user interface

=head1 DESCRIPTION

AutoLaTeX::GUI::AbstractToolPanel is a Perl module, which permits to
display a panel that launchs AutoLaTeX tools.

=head1 METHOD DESCRIPTIONS

This section contains only the methods in AbstractToolPanel.pm itself.

=over

=cut

package AutoLaTeX::GUI::AbstractToolPanel;

@ISA = qw( AutoLaTeX::GUI::WidgetUtil );
@EXPORT = qw();
@EXPORT_OK = qw();

use strict;
use vars qw(@ISA @EXPORT @EXPORT_OK $VERSION);
use Exporter;

use AutoLaTeX::Core::Util;
use AutoLaTeX::Core::IntUtils;
use AutoLaTeX::Core::Config;
use AutoLaTeX::GUI::WidgetUtil;

#------------------------------------------------------
#
# Global vars
#
#------------------------------------------------------

# Version number
my $VERSION = "8.0" ;


=pod

=item * initializeToolPanel()

Initializing the panel content before displaying.

=cut
sub initializeToolPanel() : method {
	my $self = shift;
}

=pod

=item * savePanelContent()

Save the content of this panel.
DO NOT OVERRIDE THIS FUNCTION. See
saveGUIConfiguration() instead.

=cut
sub savePanelContent() {
	my $self = shift;

	printDbg(_T("Saving tool configuration"));
	printDbgIndent ();

	my %configuration = readOnlyUserConfiguration();
	$self->saveGUIConfiguration(\%configuration);
	writeConfigFile(getUserConfigFilename(), %configuration);

	printDbgUnindent ();
}

=pod

=item * saveGUIConfiguration(\%)

Save the GUI configuration inside the specified configuration.

=over 4

=item is the configuration to fill

=back

=cut
sub saveGUIConfiguration() {
	my $self = shift;
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
