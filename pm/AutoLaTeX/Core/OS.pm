# autolatex - OS.pm
# Copyright (C) 1998-13  Stephane Galland <galland@arakhne.org>
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

OS.pm - Operating System

=head1 DESCRIPTION

Identify the current operating system.

To use this library, type C<use AutoLaTeX::Core::OS;>.

=head1 FUNCTIONS

The provided functions are:

=over 4

=cut
package AutoLaTeX::Core::OS;

$VERSION = '5.0';
@ISA = ('Exporter');
@EXPORT = qw( &getPathListSeparator &getOperatingSystem &getSupportedOperatingSystems &which
	      &touch &readlink_osindep &parseCLI &parseCLIWithExceptions &lastFileChange ) ;
@EXPORT_OK = qw();

require 5.014;
use strict;
use utf8;
use vars qw(@ISA @EXPORT @EXPORT_OK $VERSION);
use Config; # Perl configuration
use File::stat;
use File::Basename;
use File::Path qw(make_path);

my %operatingsystem = 
             (MacOS   => 'Mac',
              MSWin32 => 'Win32',
              os2     => 'OS2',
              VMS     => 'VMS',
              epoc    => 'Epoc',
              NetWare => 'Win32',
              symbian => 'Win32',
              dos     => 'OS2',
              cygwin  => 'Cygwin');

my $Is_VMS    = ($^O eq 'VMS');
my $Is_MacOS  = ($^O eq 'MacOS');
my $Is_DOSish = (($^O eq 'MSWin32') or
                ($^O eq 'dos')     or
                ($^O eq 'os2'));

# For Win32 systems, stores the extensions used for
# executable files
# For others, the empty string is used
# because 'perl' . '' eq 'perl' => easier
my @path_ext = ('');
if ($Is_DOSish) {
	if ($ENV{PATHEXT} and $Is_DOSish) {    # WinNT. PATHEXT might be set on Cygwin, but not used.
		push @path_ext, split ';', $ENV{PATHEXT};
	}
	else {
		push @path_ext, qw(.com .exe .bat); # Win9X or other: doesn't have PATHEXT, so needs hardcoded.
	}
}
elsif ($Is_VMS) { 
	push @path_ext, qw(.exe .com);
}

=pod

=item B<getPathListSeparator()>

Replies the separator of paths inside a path list.

I<Returns:> the separator.

=cut
sub getPathListSeparator() {
	return $Config{'path_sep'} || ':';
}

=pod

=item B<getOperatingSystem()>

Replies the name of the current operating system.

I<Returns:> the name.

=cut
sub getOperatingSystem() {
	return $operatingsystem{$^O} || 'Unix';
}

=pod

=item B<getSupportedOperatingSystems()>

Replies all the names of the supported operating systems.

I<Returns:> the list of operating system's names.

=cut
sub getSupportedOperatingSystems() {
	my %list = ();
	foreach my $v (values %operatingsystem) {
		$list{"$v"} = 1;
	}
	return keys %list;
}

sub expandShellCharsOnUnix(@) {
	my $t = shift;
	if ($t) {
		my @parts = File::Spec->splitdir("$t");
		foreach my $e (@parts) {
			if ($e eq '~') {
				$e = $ENV{'HOME'};
			}
			elsif ($e =~ /^~([a-zA-Z_][a-zA-Z_0-9]*)$/) {
				my @p = File::Spec->split($ENV{'HOME'});
				pop @p;
				$e = File::Spec->catdir(@p);
			}
		}
		$t = File::Spec->catfile(@parts);
		$t =~ s/\$([a-zA-Z_][a-zA-Z_0-9]*)/$ENV{$1}/g;
		$t =~ s/\$\{([a-zA-Z_][a-zA-Z_0-9]*)\}/$ENV{$1}/g;
		$t =~ s/\$\(([a-zA-Z_][a-zA-Z_0-9]*)\)/$ENV{$1}/g;
	}
	return $t;
}

sub expandShellCharsOnWindows(@) {
	my $t = shift;
	if ($t) {
		$t =~ s/\%{1,2}([a-zA-Z_][a-zA-Z_0-9]*)/$ENV{$1}/g;
		$t =~ s/\%{1,2}\{([a-zA-Z_][a-zA-Z_0-9]*)\}/$ENV{$1}/g;
		$t =~ s/\%{1,2}\(([a-zA-Z_][a-zA-Z_0-9]*)\)/$ENV{$1}/g;
	}
	return $t;
}

=pod

=item B<expandShellChars($)>

Expand the specified value with the Shell metacommands.

I<Parameters:>

=over 8

=item * the string to expand.

=back

I<Returns:> the result of the epxansion.

=cut
sub expandShellChars($) {
	my $operatingsystem = getOperatingSystem();
	if (("$operatingsystem" eq 'Unix')||(("$operatingsystem" eq 'Cygwin'))) {
		return expandShellCharsOnUnix(@_);
	}
	else {
		return expandShellCharsOnWindows(@_);
	}
}

=pod

=item B<which(@)>

Replies the paths to executable programs on systems under which the `which' program wasn't implemented in the shell.

C<which()> searches the directories of the user's C<PATH> (as returned by
C<File::Spec-E<gt>path()>), looking for executable files having the name specified
as a parameter to C<which()>. Under Win32 systems, which do not have a notion of
directly executable files, but uses special extensions such as C<.exe> and
C<.bat> to identify them, C<which()> takes extra steps to assure that you
will find the correct file (so for example, you might be searching for C<perl>,
it'll try C<perl.exe>, C<perl.bat>, etc.)

If it finds an executable with the name you specified, C<which()> will return
the absolute path leading to this executable (for example, C</usr/bin/perl> or
C<C:\Perl\Bin\perl.exe>).

If it does I<not> find the executable, it returns C<undef>.

If C<which()> is called in list context, it will return I<all> the
matches.

=over 4

=item C<short_exe_name> is the name used in the shell to call the program (for example, C<perl>).

=back

=cut
sub which(@) {
	my ($exec) = @_;

	return undef unless $exec;

	my $all = wantarray;
	my @results = ();

	# check for aliases first
	if ($Is_VMS) {
		my $symbol = `SHOW SYMBOL $exec`;
		chomp($symbol);
		if (!$?) {
			return $symbol unless $all;
			push @results, $symbol;
		}
	}
	if ($Is_MacOS) {
		my @aliases = split /\,/, $ENV{Aliases};
		foreach my $alias (@aliases) {
			# This has not been tested!!
			# PPT which says MPW-Perl cannot resolve `Alias $alias`,
			# let's just hope it's fixed
			if (lc($alias) eq lc($exec)) {
				chomp(my $file = `Alias $alias`);
				last unless $file;  # if it failed, just go on the normal way
				return $file unless $all;
				push @results, $file;
				# we can stop this loop as if it finds more aliases matching,
				# it'll just be the same result anyway
				last;
			}
		}
	}

	my @path = File::Spec->path();
	unshift @path, File::Spec->curdir if $Is_DOSish or $Is_VMS or $Is_MacOS;

	for my $base (map { File::Spec->catfile($_, $exec) } @path) {
		for my $ext (@path_ext) {
			my $file = $base.$ext;
			# print STDERR "$file\n";

			if ((-x $file or    # executable, normal case
				($Is_MacOS ||  # MacOS doesn't mark as executable so we check -e
				($Is_DOSish and grep { $file =~ /$_$/i } @path_ext[1..$#path_ext])
				# DOSish systems don't pass -x on non-exe/bat/com files.
				# so we check -e. However, we don't want to pass -e on files
				# that aren't in PATHEXT, like README.
				and -e _)
				) and !-d _)
			{                   # and finally, we don't want dirs to pass (as they are -x)

			# print STDERR "-x: ", -x $file, " -e: ", -e _, " -d: ", -d _, "\n";

				return $file unless $all;
				push @results, $file;       # Make list to return later
			}
		}
	}

	if($all) {
		return @results;
	}
	else {
		return undef;
	}
}

=pod

=item B<touch(@)>

Change the time associated to the specified files.

=cut
sub touch(@) {
	#my ($atime, $mtime);
	#$atime = $mtime = time;	
	foreach my $f (@_) {
		make_path(dirname("$f"));
		if (-e "$f") {
			utime(undef, undef, "$f");
		}
		else {
			local *FILE;
			open(*FILE, "> $f") or die("$f: $!\n");
			close(*FILE);
		}
	}
}

=pod

=item B<readlink_osindep(@)>

Try to dereference symbolic links.

=cut
sub _readlink($) {
	my $f = shift;
	while ( $f && -l "$f" ) {
		$f = readlink("$f");
	}
	return $f;
}
sub readlink_osindep(@) {
	if (wantarray) {
		my @result = ();
		foreach my $s (@_) {
			push @result, _readlink($s);
		}
		return @result;
	}
	else {
		if ($_[0]) {
			return _readlink($_[0]);
		}
		return undef;	
	}
}

=pod

=item B<parseCLI(@)>

Parse the given strings as command lines and extract each component.
The components are separated by space characters. If you want a
space character inside a component, you muse enclose the component
with quotes. To have quotes in components, you must protect them
with the backslash character.
This function expand the environment variables.

I<Note:> Every paramerter that is an associative array is assumed to be an
environment of variables that should be used prior to C<@ENV> to expand the
environment variables. The elements in the parameter are treated from the
first to the last. Each time an environment was found, it is replacing any
previous additional environment.

I<Parameters:>

=over 8

=item * c<c> are the strings to parse.

=back

I<Returns:> the array of components if one string is given as parameter; or the array of arrays of components,
each sub array corresponds to one of the given parameters.

=cut
sub parseCLI(@) {
	my %e = ();
	my @r = ();
	my $addenv = undef;
	if (@_>1) {
		foreach my $s (@_) {
			if (_ishash($s)) {
				$addenv = $s;
			}
			else {
				my @rr = _parseCLI($s,\%e,$addenv);
				push @r, \@rr;
			}
		}
		if (@r==1) {
			@r = @{$r[0]};
		}
	}
	elsif (@_>0 && !_ishash($_[0])) {
		@r = _parseCLI($_[0],\%e,$addenv);
	}
	return @r;
}

=pod

=item B<parseCLI(@)>

Parse the given strings as command lines and extract each component.
The components are separated by space characters. If you want a
space character inside a component, you muse enclose the component
with quotes. To have quotes in components, you must protect them
with the backslash character.
This function expand the environment variables.

I<Note:> Every paramerter that is an associative array is assumed to be an
environment of variables that should be used prior to C<@ENV> to expand the
environment variables. The elements in the parameter are treated from the
first to the last. Each time an environment was found, it is replacing any
previous additional environment.

I<Parameters:>

=over 8

=item * c<exceptions> are the names of the environment variables to not expand.

=item * c<c> are the strings to parse.

=back

I<Returns:> the array of components if one string is given as parameter; or the array of arrays of components,
each sub array corresponds to one of the given parameters.

=cut
sub parseCLIWithExceptions(\@@) {
	my $e = shift;
	my %ex = ();
	my $addenv = undef;
	foreach my $e (@{$e}) {
		$ex{$e} = undef;
	}
	my @r = ();
	if (@_>1) {
		foreach my $s (@_) {
			if (_ishash($s)) {
				$addenv = $s;
			}
			else {
				my @rr = _parseCLI($s,\%ex,$addenv);
				push @r, \@rr;
			}
		}
		if (@r==1) {
			@r = @{$r[0]};
		}
	}
	elsif (@_>0 && !_ishash($_[0])) {
		@r = _parseCLI($_[0],\%ex,$addenv);
	}
	return @r;
}

sub _parseCLI($$$) {
	my $text = shift;
	my $exceptions = shift;
	my $addenv = shift;
	my @r = ();
	if ($text) {
		$text =~ s/^\s+//gs;
		$text =~ s/\s+$//gs;
		if ($text) {
			my $protect = '';
			my $value = '';
			while ($text && $text =~ /^(.*?)(["']|(?:\s+)|(?:\\.)|(?:\$[a-zA-Z0-9_]+)|(?:\$\{[a-zA-Z0-9_]+\}))(.*)$/s) {
				(my $prefix, my $sep, $text) = ($1, $2, $3);
				$value .= $prefix;
				if ($sep =~ /^\\(.)$/) {
					$value .= $1;
				}
				elsif ($sep =~ /^\$(?:([a-zA-Z0-9_]+))|(?:\{([a-zA-Z0-9_]+)\})$/) {
					my $varname = $1 || $2;
					if ($protect eq '\'' || exists $exceptions->{"$varname"}) {
						$value .= $sep;
					}
					elsif ($addenv && exists $addenv->{$varname}) {
						$value .= ($addenv->{$varname} || '');
					}
					else {
						$value .= ($ENV{$varname} || '');
					}
				}
				elsif ($sep eq '"' || $sep eq '\'') {
					if (!$protect) {
						$protect = $sep;
					}
					elsif ($protect eq $sep) {
						$protect = '';
					}
					else {
						$value .= $sep;
					}
				}
				elsif ($protect) {
					$value .= $sep;
				}
				elsif ($value) {
					push @r, $value;
					$value = '';
				}
			}
			if ($text) {
				$value .= $text;
			}
			if ($value) {
				push @r, $value;
			}
		}
	}
	return @r;
}

sub _ishash($) {
	return 0 unless defined($_[0]) ;
	my $r = ref( $_[0] ) ;
	return ( $r eq "HASH" ) ;
}

=pod

=item B<lastFileChange($)>

Replies the date of the last change for the specified file.
If the file does not exist, C<undef> is replied.

=cut
sub lastFileChange($) {
	my $file = shift;
	return undef unless ($file);
	my $stats = stat("$file");
	return undef unless ($stats);
	return ($stats->mtime > $stats->ctime) ? $stats->mtime : $stats->ctime;
}


1;
__END__
=back

=head1 BUG REPORT AND FEEDBACK

To report bugs, provide feedback, suggest new features, etc. visit the AutoLaTeX Project management page at <http://www.arakhne.org/autolatex/> or send email to the author at L<galland@arakhne.org>.

=head1 LICENSE

S<GNU Public License (GPL)>

=head1 COPYRIGHT

S<Copyright (c) 1998-13 Stéphane Galland E<lt>galland@arakhne.orgE<gt>>

=head1 SEE ALSO

L<autolatex-dev>
