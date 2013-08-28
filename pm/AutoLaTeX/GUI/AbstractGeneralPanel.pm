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

AutoLaTeX::GUI::AbstractGeneralPanel - An abstract user interface

=head1 DESCRIPTION

AutoLaTeX::GUI::AbstractGeneralPanel is a Perl module, which permits to
display a panel that manages AutoLaTeX general options.

=head1 METHOD DESCRIPTIONS

This section contains only the methods in AbstractGeneralPanel.pm itself.

=over

=cut

package AutoLaTeX::GUI::AbstractGeneralPanel;

@ISA = qw( AutoLaTeX::GUI::WidgetUtil );
@EXPORT = qw();
@EXPORT_OK = qw();

require 5.014;
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
my $VERSION = "6.0" ;


=pod

=item * initializeTranslatorPanel()

Initializing the panel content before displaying.

=cut
sub initializeGeneralPanel() : method {
	my $self = shift;
}

=pod

=item * savePanelContent()

Save the content of this panel.

=cut
sub savePanelContent() {
	my $self = shift;

	my $configFilename;
	eval("\$configFilename = ".$self->attr('configuration-filename')."();");
	printDbg(formatText(_T("Saving configuration information into {}"), $configFilename));
	printDbgIndent();

	my %configuration = ();
	readConfigFile($configFilename,%configuration,1);
	
	my %updatedConfiguration = %{$self->attr('configuration')};
	my $changed = 0;
	while (my ($k,$v) = each(%updatedConfiguration)) {
		my $oldv = (exists $configuration{$k}) ? $configuration{$k} : undef;
		if ((($v)&&(!$oldv))||
		    ((!$v)&&($oldv))||
		    (($v)&&($oldv)&&
		     ("$v" ne "$oldv"))) {
			if (!$v) {
				delete $configuration{$k};
			}
			else {
				$configuration{$k} = $v;
			}
			$changed = 1;
		}
	}

	if ($changed) {
		writeConfigFile($configFilename,%configuration);
	}
	else {
		printDbg(_T("No change detected"));
	}
	printDbgUnindent();
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
