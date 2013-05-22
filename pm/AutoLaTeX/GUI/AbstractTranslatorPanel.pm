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

AutoLaTeX::GUI::AbstractTranslatorPanel - An abstract user interface

=head1 DESCRIPTION

AutoLaTeX::GUI::AbstractTranslatorPanel is a Perl module, which permits to
display a panel that manages AutoLaTeX translators.

=head1 METHOD DESCRIPTIONS

This section contains only the methods in AbstractTranslatorPanel.pm itself.

=over

=cut

package AutoLaTeX::GUI::AbstractTranslatorPanel;

@ISA = qw( AutoLaTeX::GUI::WidgetUtil );
@EXPORT = qw();
@EXPORT_OK = qw();

use strict;
use vars qw(@ISA @EXPORT @EXPORT_OK $VERSION);
use Exporter;

use AutoLaTeX::GUI::WidgetUtil;
use AutoLaTeX::Core::Util;
use AutoLaTeX::Core::Translator;
use AutoLaTeX::Core::Config;

#------------------------------------------------------
#
# Global vars
#
#------------------------------------------------------

# Version number
my $VERSION = "5.4" ;

=pod

=item * initializeTranslatorPanel()

Initializing the panel content before displaying.

This method read the list of the translators and
fill the attribute C<{'DATA'}{'translators'}>.

=cut
sub initializeTranslatorPanel() : method {
	my $self = shift;

	$self->initLocale ('autolatexgui');
	my %translators = $self->readTranslatorList();
	$self->attr('TRANSLATORS') = \%translators;
}

=pod

=item * readTranslatorList()

Replies the hastable that describes the translators

=cut
sub readTranslatorList() : method {
	my $self = shift;

	my $systemConfig = $self->attr('CONFIGURATIONS','SYSTEM') || {};
	my $userConfig = $self->attr('CONFIGURATIONS','USER') || {};
	my $projectConfig = $self->attr('CONFIGURATIONS','PROJECT') || {};
	my $config = $self->attr('CONFIGURATIONS','FULL') || {};

	my %translators = getTranslatorList(%{$config});

	setInclusionFlags(%translators,
		%{$systemConfig},
		%{$userConfig},
		%{$projectConfig});

	return %translators;
}


=pod

=item * applyInclusionsInConfiguration(\%$)

Put the translator inclusion flags into the specified configuration.
Replies if a changed was applied in the configuration

=over 4

=item the configuration data structure

=item the configuration level

=back

=cut
sub applyInclusionsInConfiguration(\%$) {
	my $self = shift;
	my $hasChanged = 0;
	my $allTrans = $self->attr('TRANSLATORS');
	while (my ($transName,$data) = each(%{$allTrans})) {
		if (defined($data->{'included'}{$_[1]})) {
			my $val = cfgToBoolean($data->{'included'}{$_[1]});
			$hasChanged = ($hasChanged)||(!$_[0]->{"$transName.include module"})||($_[0]->{"$transName.include module"} ne $val);
			$_[0]->{"$transName.include module"} = $val;
		}
	}
	$self->localeDbg(_T("No change detected")) unless ($hasChanged);
	return $hasChanged;
}

=pod

=item * savePanelContent()

Save the content of this panel.

=cut
sub savePanelContent() : method {
	my $self = shift;
	my %configuration;

	# System level
	if ($self->isAdminUser()) {
		$self->localeDbg(_T("Saving system configuration about translators"));
		printDbgIndent();
		%configuration = readOnlySystemConfiguration(1);
		if ($self->applyInclusionsInConfiguration(\%configuration,'system')) {
			writeConfigFile(getSystemConfigFilename(), %configuration);
		}
		printDbgUnindent();
	}

	# User level
	$self->localeDbg(_T("Saving user configuration about translators"));
	printDbgIndent();
	%configuration = readOnlyUserConfiguration(1);
	if ($self->applyInclusionsInConfiguration(\%configuration,'user')) {
		writeConfigFile(getUserConfigFilename(), %configuration);
	}
	printDbgUnindent();

	# Project level
	if ($self->hasProject()) {
		$self->localeDbg(_T("Saving project configuration about translators"));
		printDbgIndent();
		%configuration = %{readOnlyProjectConfiguration($self->attr('CONFIGURATIONS','PROJECT','__private__','input.project directory'))};
		if ($self->applyInclusionsInConfiguration(\%configuration,'project')) {
			writeConfigFile(getProjectConfigFilename(), %configuration);
		}
		printDbgUnindent();
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
