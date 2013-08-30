# Copyright (C) 2013  Stephane Galland <galland@arakhne.org>
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

AutoLaTeX::Interpreter::python - A Python interpreter

=head1 DESCRIPTION

AutoLaTeX::Interpreter::python is a Perl module, which permits to
run Python scripts.

=head1 METHOD DESCRIPTIONS

This section contains only the methods in python.pm itself.

=over

=cut

package AutoLaTeX::Interpreter::python;

@ISA = qw( AutoLaTeX::Interpreter::AbstractInterpreter );
@EXPORT = qw();
@EXPORT_OK = qw();

require 5.014;
use strict;
use utf8;
use vars qw(@ISA @EXPORT @EXPORT_OK $VERSION);
use Exporter;
use Carp;
use Scalar::Util qw(looks_like_number);

use AutoLaTeX::Interpreter::AbstractInterpreter;
use AutoLaTeX::Core::Util;

#------------------------------------------------------
#
# Global vars
#
#------------------------------------------------------

# Version number
my $VERSION = "1.0" ;


=pod

=item * new()

Constructor

=cut
sub new() : method {
	my $proto = shift;
	my $class = ref($proto) || $proto;
	my $self = bless( $class->SUPER::new(), $class);
	return $self;
}


sub _to_python($) {
	my $value = shift;
	if (defined($value)) {
		if (isArray($value)) {
			my $array = '';
			foreach my $v (@{$value}) {
				if ($array) {
					$array .= ', ';
				}
				$array .= &_to_python($v);
			}
			return "[ $array ]";
		}
		elsif (isHash($value)) {
			my $array = '';
			while (my ($k,$v) = each(%{$value})) {
				if ($array) {
					$array .= ', ';
				}
				$array .= '"'.str2language("$k").'": ';
				$array .= &_to_python($v);
			}
			return "{ $array }";
		}
		elsif (looks_like_number($value)) {
			return "$value";
		}
		else {
			return '"'.str2language("$value").'"';
		}
	}
	return 'None';
}

=pod

=item * run($)

Run the given code.

=cut
sub run($) : method {
	my $self = shift;
	my $code = shift || confess("no code");
	my $fullcode = "# coding=utf8\n";
	while (my ($name,$value) = each(%{$self->{'global'}})) {
		$fullcode .= "$name = "._to_python($value)."\n";
	}
	$fullcode .= "\n\n\n$code";
	runCommandOrFailFromInput($fullcode, 'python');
}


1;
__END__

=back

=head1 COPYRIGHT

(c) Copyright 2013 Stephane Galland E<lt>galland@arakhne.orgE<gt>, under GPL.

=head1 AUTHORS

=over

=item *

Conceived and initially developed by Stéphane Galland E<lt>galland@arakhne.orgE<gt>.

=back

=head1 SEE ALSO

L<autolatex>
