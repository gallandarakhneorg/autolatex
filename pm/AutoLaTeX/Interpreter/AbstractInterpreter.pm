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

AutoLaTeX::Interpreter::AbstractInterpreter - An abstract script interpreter

=head1 DESCRIPTION

AutoLaTeX::Interpreter::AbstractInterpreter is a Perl module, which permits to
create script interpreters

=head1 METHOD DESCRIPTIONS

This section contains only the methods in AbstractInterpreter.pm itself.

=over

=cut

package AutoLaTeX::Interpreter::AbstractInterpreter;

@ISA = qw( Exporter );
@EXPORT = qw();
@EXPORT_OK = qw();

require 5.014;
use strict;
use utf8;
use vars qw(@ISA @EXPORT @EXPORT_OK $VERSION);
use Exporter;
use Carp;

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
	my $parent = ref($proto) && $proto ;

	my $self ;
	if ( $parent ) {
		%{$self} = %{$parent} ;
	}
	else {
		$self = { 'global' => {} };
	}
	bless( $self, $class );
	return $self;
}

=pod

=item * define_global_variable($$)

Define the value of a global variable.

=cut
sub define_global_variable($$) : method {
	my $self = shift;
	my $name = shift || confess("no variable name");
	my $value = shift;
	$self->{'global'}{"$name"} = $value;
}

=pod

=item * run($)

Run the given code.

=cut
sub run($) : method {
	confess("You must implement the method run().");
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
