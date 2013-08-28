# autolatex - IntUtils.pm
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

To use this library, type C<use AutoLaTeX::Core::IntUtils;>.

=head1 FUNCTIONS

The provided functions are:

=over 4

=cut
package AutoLaTeX::Core::IntUtils;

our @ISA = qw( Exporter );
our @EXPORT = qw( &_T &initTextDomain &getCurrentLocale &getCurrentLanguage &getCurrentCodeset &getActiveTextDomains );
our @EXPORT_OK = qw();

require 5.014;
use strict;
use vars qw(@ISA @EXPORT @EXPORT_OK $VERSION);
use Exporter;

use Carp;
use Locale::gettext;
use POSIX;     # Needed for setlocale()

our $VERSION = '1.0';

my @ACTIVE_DOMAINS = ();

=pod

=item B<_T($)>

Marker for the internationalization.
The parameter of this function is a string that
may be localized.
Replies the localized string that is corresponding
to the given parameter.

CAUTION: tries to find a translation in all the initialized
text domain (see initTextDomain function).

=cut
sub _T($) {
	my $previous;
	foreach my $domain (@ACTIVE_DOMAINS) {
		#print "SEARCH FOR '".$_[0]."' in $domain\n";
		my $p = textdomain($domain);
		$previous = $p unless $previous;
		my $translation = gettext($_[0]);
		#print ">$translation<\n";
		if ($translation && $translation ne $_[0]) {
			return $translation;
		}
	}
	if ($previous) {
		textdomain($previous);
	}
	return $_[0];
}

=pod

=item B<initTextDomain($$)>

Initialize the internationalization domain.

=over 4

=item domain: is the name of the text domain to use for internationalization.

=item directory: is the directory where '.mo' (compiled '.po') could be found for the domain.

=item codeset: is the code set used to encode the po files.

=cut
sub initTextDomain($$;$) {
	my $domain = shift || confess("initTextDomain must takes a domain as first parameter");
	my $directory = shift || confess("initTextDomain must takes a directory as second parameter");
	my $codeset = shift;
	bindtextdomain($domain, $directory);
	if ($codeset) {
		bind_textdomain_codeset($domain, $codeset);
	}
	textdomain($domain);
	push @ACTIVE_DOMAINS, $domain;
}

=pod

=item B<getActiveTextDomains()>

Replies the active text domains.

=cut
sub getActiveTextDomains() {
	my @copy = @ACTIVE_DOMAINS;
	return \@copy;
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
