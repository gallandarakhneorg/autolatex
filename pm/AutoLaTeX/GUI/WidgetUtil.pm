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

AutoLaTeX::GUI::WidgetUtil - A generic widget utility class

=head1 DESCRIPTION

AutoLaTeX::GUI::WidgetUtil is a Perl module, which provides
utility methods for widgets.

=head1 METHOD DESCRIPTIONS

This section contains only the methods in WidgetUtil.pm itself.

=over

=cut

package AutoLaTeX::GUI::WidgetUtil;

@ISA = ('Exporter');
@EXPORT = qw();
@EXPORT_OK = qw();

use strict;
use vars qw(@ISA @EXPORT @EXPORT_OK $VERSION);
use Exporter;

use File::Basename;
use File::Spec;
use AutoLaTeX::Core::Util;
use AutoLaTeX::Core::Locale;

#------------------------------------------------------
#
# Global vars
#
#------------------------------------------------------

# Version number
my $VERSION = "5.1" ;

# List of locales
my %LOCALES = ();

#------------------------------------------------------
#
# Functions
#
#------------------------------------------------------

=pod

=item * initLocale($;$)

Initialize a locale for this object.

=over 4

=item the name of the locale domain

=item the directory where are stored the locale files. If not given, assume "autolatex_dir/po"

=back

=cut
sub initLocale($;$) {
	my $self = shift;
	my $domain = shift || die('you must specify a locale domain');;
	my $directory = shift;

	unless (exists $LOCALES{"$domain"}) {
		$directory = File::Spec->catfile (getAutoLaTeXDir(), 'po')
			unless ($directory);
		my $locale = AutoLaTeX::Core::Locale->new($directory,$domain);
		$LOCALES{"$domain"} = $locale;
	}
}

=pod

=item * localeGet($@)

Replies a localized message.

The substrings C<$0>, C<$1>, C<$2>... will be substituted by
the corresponding values passed in parameters after the message id.

The substrings C<${0}>, C<${1}>, C<${2}>... will be substituted by
the corresponding values passed in parameters after the message id.

The substrings C<#0>, C<#1>, C<#2>... will be substituted by
the corresponding values passed in parameters after the message id.

The substrings C<#{0}>, C<#{1}>, C<#{2}>... will be substituted by
the corresponding values passed in parameters after the message id.

The substrings C<{}> will be replaced by the value passed in parameters
that corresponds to the C<{}>, e.g. the first C<{}> will be replaced by the
first value, the second C<{}> by the second value...

=over 4

=item the id of the string

=item the list of substitution values.

=back

I<Returns:> the localized string.

=cut
sub localeGet($@) {
	my $self = shift;
	my $msgId = shift;
	if (%LOCALES) {
		my $msg;
		foreach my $localeServer (values %LOCALES) {
			$msg = $localeServer->getRaw ($msgId);
			if (($msg)&&($msg ne $msgId)) {
				return localeSubstitute ($msg,@_);
			}
		}
	}
	return localeSubstitute($msgId,@_);
}

=pod

=item * localeDbg($@)

Equivalent to printDbg($self->localeGet).

=cut
sub localeDbg($@) {
	my $self = shift;
	my $msgId = shift;
	printDbg($self->localeGet($msgId,@_));
}

=pod

=item * localeErr($@)

Equivalent to printErr($self->localeGet).

=cut
sub localeErr($@) {
	my $self = shift;
	my $msgId = shift;
	printErr($self->localeGet($msgId,@_));
}

=pod

=item * setAdminUser($)

Set if the current user is an administrator.

=cut
sub setAdminUser($) : method {
	my $self = shift;
	$self->attr('isAdmin') = $_[0];
}

=pod

=item * isAdminUser()

Replies if the current user is an administrator.

=cut
sub isAdminUser() : method {
	my $self = shift;
	return ($self->attr('isAdmin'));
}

=pod

=item * hasProject()

Replies if this panel contains the configuration of a project or not.

=cut
sub hasProject() : method {
	my $self = shift;
	return (($self->hasattr('CONFIGURATIONS','PROJECT'))&&
		(defined($self->attr('CONFIGURATIONS','PROJECT'))));
}

=pod

=item * attr(@)

Replies the given attribute.

=over 4

=item the name of the attribute.

=back

=cut
sub attr(@) : lvalue method {
	my $self = shift;
	die("you must specified a name for the attribute\n") unless (@_);
	$self->{'AUTOLATEX_ATTR'} = {} unless (exists $self->{'AUTOLATEX_ATTR'});
	$a = $self->{'AUTOLATEX_ATTR'};
	my $lastname = pop @_;
	foreach my $name (@_) {
		$a->{"$name"} = {} unless ((exists $a->{"$name"})&&(isHash($a->{"$name"})));
		$a = $a->{"$name"};
	}
	$a->{"$lastname"};
}

=pod

=item * hasattr(@)

Replies if the given attribute exists.

=over 4

=item the name of the attribute.

=back

=cut
sub hasattr(@) : method {
	my $self = shift;
	die("you must specified a name for the attribute\n") unless (@_);
	return undef unless (exists $self->{'AUTOLATEX_ATTR'});
	$a = $self->{'AUTOLATEX_ATTR'};
	my $lastname = pop @_;
	foreach my $name (@_) {
		return undef unless ((exists $a->{"$name"})&&(isHash($a->{"$name"})));
		$a = $a->{"$name"};
	}
	return exists $a->{"$lastname"};
}

=pod

=item * deleteattr(@)

Delete the given attribute if it exists.

=over 4

=item the name of the attribute.

=back

=cut
sub deleteattr(@) : method {
	my $self = shift;
	die("you must specified a name for the attribute\n") unless (@_);
	my $oldvalue = undef;
	return $oldvalue unless (exists $self->{'AUTOLATEX_ATTR'});
	$a = $self->{'AUTOLATEX_ATTR'};
	my $lastname = pop @_;
	foreach my $name (@_) {
		return $oldvalue unless ((exists $a->{"$name"})&&(isHash($a->{"$name"})));
		$a = $a->{"$name"};
	}
	if (exists $a->{"$lastname"}) {
		$oldvalue = $a->{"$lastname"};
		delete $a->{"$lastname"};
	}
	return $oldvalue;
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
	return undef;
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
