# autolatex - Locale.pm
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

Locale.pm - Internationalization Utilities

=head1 DESCRIPTION

Provides a set of utilities for internationalization.

To use this library, type C<use AutoLaTeX::Core::Locale;>.

=head1 FUNCTIONS

The provided functions are:

=over 4

=cut
package AutoLaTeX::Core::Locale;
require 5.004;

our @ISA = qw( Exporter );
our @EXPORT = qw( &getCurrentLocale &getCurrentLanguage &locGet &locPrint &localeInit 
		  &localeSubstitute _T );
our @EXPORT_OK = qw();

use strict;
use vars qw(@ISA @EXPORT @EXPORT_OK $VERSION);
use Exporter;

use Locale::gettext;
use POSIX; # Needed for setlocale()
use File::Spec;

our $VERSION = '5.1';
my $localServer;

BEGIN{
	$localServer = undef;
	setlocale(LC_ALL, "");
}

sub localeInit($;$) {
	my $directory = shift;
	my $domain = shift;
	unless ($localServer) {
		$localServer = AutoLaTeX::Core::Locale->new(File::Spec->catfile($directory,'po'),$domain);
	}
	return $localServer;
}

# Marker for localized texts
sub _T {
	$_[0];
}

=pod

=item B<localeSubstitute($@)>

Replies the locale string after substitution.

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
sub localeSubstitute($@) {
	my $localizedMsg = shift;
	if (@_) {
		for(my $i=0; $i<@_; $i++) {
			$localizedMsg =~ s/[\$\#]\Q{$i}\E/$_[$i]/g;
			$localizedMsg =~ s/[\$\#]\Q$i\E/$_[$i]/g;
		}
		my $i=0;
		$localizedMsg =~ s/\Q{}\E/my $v;if ($i<@_) {$v=$_[$i]||'';$i++;} else {$v="{}";}"$v";/eg;
	}
	return $localizedMsg;
}

=pod

=item B<getCurrentLocale()>

Replies the current locale.

=cut
sub getCurrentLocale() {
	my $lang = $ENV{'LC_ALL'} || $ENV{'LANG'};
	if ($lang =~ /^([a-zA-Z]+_[a-zA-Z]+)/) {
		return "$1";
	}
	elsif ($lang =~ /^([a-zA-Z]+)/) {
		return "$1";
	}
	return undef;
}

=pod

=item B<getCurrentCodeset()>

Replies the current codeset.

=cut
sub getCurrentCodeset() {
	my $lang = $ENV{'LC_ALL'} || $ENV{'LANG'};
	if ($lang =~ /^[a-zA-Z]+_[a-zA-Z]+\.(.*)$/) {
		return "$1";
	}
	elsif ($lang =~ /^[a-zA-Z]+\.(.*)$/) {
		return "$1";
	}
	return undef;
}

=pod

=item B<getCurrentLangage()>

Replies the current language.

=cut
sub getCurrentLanguage() {
	my $lang = $ENV{'LC_ALL'} || $ENV{'LANG'};
	if ($lang =~ /^([a-zA-Z]+)_[a-zA-Z]+/) {
		return "$1";
	}
	elsif ($lang =~ /^([a-zA-Z]+)/) {
		return "$1";
	}
	return undef;
}

=pod

=item B<locGet($@)>

Replies the locale string.

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
sub locGet($@) {
	my $msgId = shift;
	die("locale server not set") unless ($localServer);
	return $localServer->get ($msgId, @_);
}

=pod

=item B<locPrint($@)>

Equivalent to print locGet

=cut
sub locPrint($@) {
	my $msgId = shift;
	print locGet($msgId, @_);
}

#-----------------------------------------
# OO API
#-----------------------------------------

sub new($;$) : method {
	my $proto = shift;
	my $class = ref($proto) || $proto;

	my $self = bless({}, $class) ;

	my $directory = shift;
	$self->{'domain'} = shift || 'autolatex';

	die('no autolatex directory found\n') unless ($directory);

	$self->{'server'} = Locale::gettext->domain_raw ($self->{'domain'});

	$self->{'server'}->codeset(getCurrentLocale());

	$self->{'directory'} = $directory;
	$self->{'server'}->dir ($self->{'directory'});

	$self->{'server'}->codeset(getCurrentLocale());

	return $self;
}

=pod

=item B<getLocale()>

Replies the locale used by this object.

=cut
sub getLocale() : method {
	my $self = shift;
	my $locale = $self->{'server'}->codeset();
	$locale = getCurrentLocale() unless ($locale);
	return $locale;
}

=pod

=item B<getLanguage()>

Replies the language used by this object.

=cut
sub getLanguage() {
	my $self = shift;
	my $locale = $self->getLocale();
	if (($locale)&&($locale =~ /^(.+?)_.+$/)) {
		return "$1";
	}
	return $locale;	
}

=pod

=item B<getCountry()>

Replies the country used by this object.

=cut
sub getCountry() : method {
	my $self = shift;
	my $locale = $self->getLocale();
	if (($locale)&&($locale =~ /^.+_(.+?)$/)) {
		return "$1";
	}
	return '';	
}

=pod

=item B<get($@)>

Replies the locale string.

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
sub get($@) : method {
	my $self = shift;
	my $msgId = shift;
	my $localizedMsg = $self->getRaw ($msgId);
	# Substitution
	return $self->substitute($localizedMsg,@_);
}

=pod

=item B<getRaw($@)>

Replies the locale without subsitution.

=over 4

=item the id of the string

=back

I<Returns:> the localized string.

=cut
sub getRaw($) : method {
	my $self = shift;
	my $msgId = shift;
	return $self->{'server'}->get ($msgId);
}

=pod

=item B<substitute($@)>

Replies the locale string after substitution.

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
sub substitute($@) {
	my $self = shift;
	my $msgId = shift;
	return localeSubstitute($msgId,@_);
}

1;
__END__
=back

=head1 BUG REPORT AND FEEDBACK

To report bugs, provide feedback, suggest new features, etc. visit the AutoLaTeX Project management page at <http://www.arakhne.org/autolatex/> or send email to the author at L<galland@arakhne.org>.

=head1 LICENSE

S<GNU Public License (GPL)>

=head1 COPYRIGHT

S<Copyright (c) 2007-13 Stéphane Galland E<lt>galland@arakhne.orgE<gt>>

=head1 SEE ALSO

L<autolatex-dev>
