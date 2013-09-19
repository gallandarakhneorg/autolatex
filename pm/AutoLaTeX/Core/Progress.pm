# autolatex - Progress.pm
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

Progress.pm - Implementation of a progress indicator

=head1 DESCRIPTION

Provides a tool to show the progress of the tasks.

To use this library, type C<use AutoLaTeX::Core::Progress;>.

=head1 GETTING STARTED

=head2 Initialization

To create a progress tool, say something like this:

    use AutoLaTeX::Core::Progress;

    my $max = 100;
    my $progress = AutoLaTeX::Core::Progress->new($max) ;

...or something similar.

=head1 METHOD DESCRIPTIONS

This section contains only the methods in Progress.pm itself.

=over

=cut
package AutoLaTeX::Core::Progress;

our @ISA = qw( Exporter );
our @EXPORT = qw( );
our @EXPORT_OK = qw();

require 5.014;
use strict;
use utf8;
use vars qw(@ISA @EXPORT @EXPORT_OK $VERSION);
use Exporter;
use Carp;
use AutoLaTeX::Core::IntUtils;
use AutoLaTeX::Core::Util qw($INTERNAL_MESSAGE_PREFIX);

our $VERSION = '3.0';

#------------------------------------------------------
#
# Constructor
#
#------------------------------------------------------

sub new(;$) : method {
	my $proto = shift;
	my $class = ref($proto) || $proto;
	my $parent = ref($proto) && $proto ;
	my $max = $_[0];
	if (!defined($max) || $max<0) {
		$max = 100;
	}
	my $self;
	if ( $parent ) {
		%{$self} = %{$parent} ;
	}
	else {
		$self = {
			'child' => undef,
			'max' => $max,
			'value' => 0,
			'bar-width' => 40,
			'comment' => '',
			'comment-to-display' => '',
			'previous-message-size' => 0,
			'carriage-return' => 1,
		};
	}
	bless( $self, $class );

	return $self;
}

sub _newChild($$$) : method {
	my $proto = shift;
	my $class = ref($proto) || $proto;
	my $parent = ref($proto) && $proto ;
	my $self;
	if ( $parent ) {
		%{$self} = %{$parent} ;
	}
	else {
		$self = {
			'child' => undef,
			'value' => 0,
			'parent' => $_[0],
			'min-in-parent' => $_[1],
			'max-in-parent' => $_[2],
			'max' => 0,
			'comment' => '',
		};
	}
	bless( $self, $class );

	return $self;
}

=pod

=item * setCarriageReturn($)

Enable or disable the use of the carraige-return character
C<\r> at the end of the lines. If the carriage-return
character is not used, the new-line character C<\n> is
used.

=over 4

=item B<use_carriage_return>

=over

=cut
sub setCarriageReturn($) : method {
	my $self = shift;
	$self->{'carriage-return'} = shift;
}

=pod

=item * getCarriageReturn()

Replies if the carriage-return character is used at the end
of the output lines.

=cut
sub getCarriageReturn() : method {
	my $self = shift;
	return $self->{'carriage-return'};
}

=pod

=item * setBarWidth($)

Set the number of characters for rendering the progress bar.

=over 4

=item B<width> is the number of characters of the bar.

=over

=cut
sub setBarWidth($) : method {
	my $self = shift;
	my $width = shift;
	if ($self->{'parent'}) {
		$self->{'parent'}->setBarWidth($width);
	}
	else {
		$self->{'bar-width'} = $width;
	}
}

=pod

=item * getBarWidth()

Replies the number of characters for rendering the progress bar.

=cut
sub getBarWidth() : method {
	my $self = shift;
	if ($self->{'parent'}) {
		return $self->{'parent'}->getBarWidth();
	}
	else {
		return $self->{'bar-width'};
	}
}

=pod

=item * setComment($)

Set the comment associated to the progress process.

=over 4

=item B<label> is the comment text.

=over

=cut
sub setComment($) : method {
	my $self = shift;
	my $label = shift || '';
	$self->{'comment'} = $label || '';
	my $c = '';
	my $p = $self;
	while ($p && $p->{'parent'}) {
		if (!$c && $p->{'comment'}) {
			$c = $p->{'comment'};
		}
		$p = $p->{'parent'};
	}
	if ($p && $p->{'comment-to-display'} ne $c) {
		$self->{'comment-to-display'} = $c;
		$self->_report();
		return 1;
	}
	return 0;
}

=pod

=item * getComment()

Replies the comment in the progress bar.

=cut
sub getComment() : method {
	my $self = shift;
	if ($self->{'parent'}) {
		return $self->{'parent'}->getComment();
	}
	else {
		return $self->{'comment-to-display'};
	}
}

=pod

=item * setMax()

Set the maximal value. It must be greater than the previous
value of max. This function does not output on the console.

=cut
sub setMax($) : method {
	my $self = shift;
	my $max = shift;
	if ($max>$self->{'max'}) {
		$self->{'max'} = $max;
	}
}

=pod

=item * getMax()

Replies the maximal value.

=cut
sub getMax() : method {
	my $self = shift;
	return $self->{'max'};
}

=pod

=item * getValue()

Replies the current value.

=cut
sub getValue() : method {
	my $self = shift;
	return $self->{'value'};
}

=pod

=item * setValue($)

Change the progress value and display the progress message.

=over 4

=item B<value> is the current value of the progress indicator.

=back

Returns a boolean value that indicates if something was setValueed.

=cut
sub setValue($;$) : method {
	my $self = shift;
	my $value = shift;
	my $comment = shift;
	my $max = $self->getMax();
	my $currentValue = $self->getValue();
	my $reported = undef;
	confess('undef $value') unless (defined($value));
	if ($value>$currentValue) {
		$self->_set_value($value);
		$currentValue = $self->getValue();
		# Close any child progress
		if ($self->{'child'}) {
			my $mip = $self->{'child'}{'max-in-parent'};
			if ($currentValue>=$mip) {
				$reported = $self->_disconnectChildProgress();
			}
		}
		# Notify parent
		if ($self->{'parent'}) {
			my $range = $self->{'max-in-parent'} - $self->{'min-in-parent'};
			my $parent_value = ($value * $range) / $max;
			$parent_value += $self->{'min-in-parent'};
			if (!defined($comment) && $self->{'comment'}) {
				$comment = $self->{'comment'};
			}
			my $reported2 = $self->{'parent'}->setValue($parent_value, $comment);
			$reported = $reported || $reported2;
		}
		# Change the comment to be displayed
		elsif (defined($comment) && $comment ne $self->{'comment-to-display'}) {
			$self->{'comment-to-display'} = $comment;
			$reported = undef;
		}
		# Force reporting
		if (!$reported) {
			$reported = $self->_report();
		}
	}
	return $reported ;
}

sub _set_value($) : method {
	my $self = shift;
	my $value = shift;
	if ($value>=$self->{'max'}) {
		$self->{'value'} = $self->{'max'};
	}
	else {
		$self->{'value'} = $value;
	}
}

sub _report() : method {
	my $self = shift;
	my $value = $self->getValue();
	my $max = $self->getMax();
	if (!$self->{'parent'}) {
		my $message = "[".$self->_formatPercent($value, $max)."] ".$self->_formatBar($value, $max);
		if ($self->{'comment-to-display'}) {
			$message .= ' '.$self->{'comment-to-display'};
		}
		my $l = length($message);
		my $tmp_l = $l;
		while ($tmp_l<$self->{'previous-message-size'}) {
			$message .= ' ';
			$tmp_l++;
		}
		$self->{'previous-message-size'} = $l;
		if (!$self->{'carriage-return'} || ($value>=$max)) {
			print STDOUT "$message\n";
		}
		else {
			print STDOUT "$message\r";
		}
		$INTERNAL_MESSAGE_PREFIX = "\n";
		return 1;
	}
	return undef;
}

sub _formatPercent($$) : method {
	my $self = shift;
	my $value = shift;
	my $max = shift;
	my $percent = int(($value * 100) / $max);
	while (length($percent)<3) {
		$percent = " $percent";
	}
	return "$percent\%";
}

sub _formatBar($$) : method {
	my $self = shift;
	my $value = shift;
	my $max = shift;
	my $bar_width = $self->getBarWidth();
	my $nchars = int(($value * $bar_width) / $max);
	my $i = 0;
	my $bar = '';
	while ($i<$nchars) {
		$bar .= '#';
		$i++;
	}
	while ($i<$bar_width) {
		$bar .= '.';
		$i++;
	}
	return $bar;
}

sub _disconnectChildProgress() : method {
	my $self = shift;
	if ($self->{'child'}) {
		my $max_in_parent = $self->{'child'}{'max-in-parent'};
		$self->{'child'} = undef;
		return $self->setValue($max_in_parent);
	}
	return undef;
}

=pod

=item * subProgress($$)

Create a subtask.

=over 4

=item B<size> (optional) is the size of the subtask in this progress. If not given, the rest of the parent task is covered by the sub task.

=back

Replies the subtask progress object.

=cut
sub subProgress(;$) : method {
	my $self = shift;
	my $size = shift;

	my $parent_max = $self->getMax();
	my $min_in_parent = $self->getValue();

	if (!defined($size) || $size<0) {
		$size = $parent_max - $min_in_parent;
	}

	my $max_in_parent = $min_in_parent + $size;
	if ($max_in_parent>$parent_max) {
		$max_in_parent = $parent_max;
	}

	$self->{'child'} = AutoLaTeX::Core::Progress->_newChild(
				$self,
				$min_in_parent,
				$max_in_parent);

	return $self->{'child'};
}

=pod

=item * increment(;$)

Increment the current value by the given amount, or by 1 if the amount is not given or invalid.

=cut
sub increment(;$) : method {
	my $self = shift;
	my $inc = shift;
	if (!defined($inc) || $inc<=0) {
		$inc = 1;
	}
	my $value = $self->getValue();
	$self->setValue($value+$inc);
}

=pod

=item * stop()

Stop the progress.

=cut
sub stop() : method {
	my $self = shift;
	my $max = $self->getMax();
	$self->setValue($max);
}

=pod

=item * debug()

Output the state of this progress.

=cut
sub debug(;$) : method {
	my $self = shift;
	my $level = shift || 0;
	printf STDERR ("%s[\%3d] value: 0<=\%f<=\%f\n", $INTERNAL_MESSAGE_PREFIX, $level, $self->{'value'}, $self->{'max'});
	$INTERNAL_MESSAGE_PREFIX = '';
	if ($self->{'parent'}) {
		my $parent_value = $self->{'parent'}->getValue();
		printf STDERR ("[\%3d] in-parent: \%f<=%f<=\%f\n", $level, $self->{'min-in-parent'}, $parent_value, $self->{'max-in-parent'});
	}
	else {
		printf STDERR ("[\%3d] comment: \%s\n", $level, $self->{'comment'});
	}
	if ($self->{'child'}) {
		$self->{'child'}->debug($level+1);
	}
}

1;
__END__
=back

=head1 BUG REPORT AND FEEDBACK

To report bug, provide feedback, suggest new features, etc. visit the AutoLaTeX Project management page at <http://www.arakhne.org/autolatex/> or send email to the author at L<galland@arakhne.org>.

=head1 LICENSE

S<GNU Public License (GPL)>

=head1 COPYRIGHT

S<Copyright (c) 2013 Stéphane Galland E<lt>galland@arakhne.orgE<gt>>

=head1 SEE ALSO

L<autolatex-dev>
