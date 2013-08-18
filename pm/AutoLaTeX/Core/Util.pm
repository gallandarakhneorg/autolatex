# autolatex - Util.pm
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

Util.pm - Utilities

=head1 DESCRIPTION

Provides a set of general purpose utilities.

To use this library, type C<use AutoLaTeX::Core::Util;>.

=head1 FUNCTIONS

The provided functions are:

=over 4

=cut
package AutoLaTeX::Core::Util;

$VERSION = '2.0';
@ISA = ('Exporter');
@EXPORT = qw( &isHash &isArray &removeFromArray &arrayContains &getAutoLaTeXDir
              &getAutoLaTeXName &getAutoLaTeXLaunchingName &getAutoLaTeXVersion
              &setAutoLaTeXInfo &showManual &printDbg &printErr &printWarn &setDebugLevel 
	      &getDebugLevel &printDbgFor &dumpDbgFor &arrayIndexOf &printDbgIndent
	      &printDbgUnindent &runCommandOrFail &runSystemCommand
              &notifySystemCommandListeners &locDbg &exitDbg &addSlashes
	      &readFileLines &writeFileLines &runCommandOrFailRedirectTo
	      &runCommandSilently &removePathPrefix &trim ) ;
@EXPORT_OK = qw();

use strict;
use vars qw(@ISA @EXPORT @EXPORT_OK $VERSION);

use File::Spec;
use POSIX ":sys_wait_h";
use Carp;
use Data::Dumper;

use AutoLaTeX::Core::Locale;

my $autoLaTeXName = undef;
my $autoLaTeXDirectory = undef;
my $autoLaTeXLaunchingName = undef;
my $autoLaTeXVersion = "$VERSION or higher";
my $debugLevel = 0;
my $dbgIndent = 0;
my %runningChildren = ();
my $lastListenerCheck = 0;

=pod

=item B<getAutoLaTeXDir()>

Replies the location of the main AutoLaTeX script.
This value must be set with a call to setAutoLaTeXInfo().

I<Returns:> the AutoLaTeX main directory.

=cut
sub getAutoLaTeXDir() {
	return $autoLaTeXDirectory;
}

=pod

=item B<getAutoLaTeXName()>

Replies the base filename of the main AutoLaTeX script.
This value must be set with a call to setAutoLaTeXInfo().

I<Returns:> the AutoLaTeX main script filename.

=cut
sub getAutoLaTeXName() {
	return $autoLaTeXName;
}

=pod

=item B<getAutoLaTeXLaunchingName()>

Replies the base filename of the command which permits
to launch AutoLaTeX. It could differ from the AutoLaTeX name
due to several links.
This value must be set with a call to setAutoLaTeXInfo().

I<Returns:> the AutoLaTeX command name.

=cut
sub getAutoLaTeXLaunchingName() {
	return $autoLaTeXLaunchingName;
}

=pod

=item B<getAutoLaTeXVersion()>

Replies the current version of AutoLaTeX.
This number is extracted from the VERSION filename if
it exists.
This value must be set with a call to setAutoLaTeXInfo().

I<Returns:> the AutoLaTeX version number.

=cut
sub getAutoLaTeXVersion() {
	return $autoLaTeXVersion;
}

=pod

=item B<setAutoLaTeXInfo($$$)>

Set the information about the main AutoLaTeX script.
This function should only be could by the AutoLaTeX main script.

I<Parameters:>

=over 8

=item * the name of the command typed on the command line.

=item * the name of the main script.

=item * the path where the main script is located.

=back

=cut
sub setAutoLaTeXInfo($$$) {
	$autoLaTeXLaunchingName = "$_[0]";
	$autoLaTeXName = "$_[1]";
	$autoLaTeXDirectory = File::Spec->rel2abs("$_[2]");

	# Set the local directory
	localeInit("$autoLaTeXDirectory");

	# Detect the version number
	my $versionFile = File::Spec->catfile($autoLaTeXDirectory,'VERSION');
	if (-f "$versionFile") {
		if (-r "$versionFile") {
			local *VERSIONFILE;
			open(*VERSIONFILE, "< $versionFile") or die("$versionFile: $!\n");
			while (my $line = <VERSIONFILE>) {
				if ($line =~ /^\s*autolatex\s+(.*?)\s*$/i) {
					$autoLaTeXVersion = "$1";
					last;
				}
			}
			close(*VERSIONFILE);
		}
		else {
			print STDERR locGet("No read access to the VERSION file of AutoLaTeX. AutoLaTeX should not be properly installed. Assuming version: {}\n",$autoLaTeXVersion);
		}
	}
	else {
		print STDERR locGet("Unable to find the VERSION file of AutoLaTeX. AutoLaTeX should not be properly installed. Assuming version: {}\n", $autoLaTeXVersion);
	}
}

=pod

=item B<showManual(@)>

Display the manual page extracted from the specified POD file.

I<Parameters:>

=over 8

=item * the components of the path to the POD file to use.

=back

I<Returns:> NEVER RETURN.

=cut
sub showManual(@) {
	my $pod;
	# Try to localize
	my $filename = pop @_;
	my $ext = '';
	if ($filename =~ /^(.*)(\.pod)$/i) {
		$ext = "$2";
		$filename = "$1";
	}

	my $currentLocale = getCurrentLocale();
	my $currentLang = getCurrentLanguage();
	
	{
		my ($localePod,$localeLang);
		local *DIR;
		opendir(*DIR,File::Spec->catfile(@_))
			or die(locGet(_T("no manual page found\n")));
		while (my $file = readdir(*DIR)) {
			if (($file ne '.')&&($file ne '..')) {
				if ($file =~ /^\Q$filename\E[._\-]\Q$currentLocale$ext\E$/) {
					$localePod = $file;
				}
				if ($file =~ /^\Q$filename\E[._\-]\Q$currentLang$ext\E$/) {
					$localeLang = $file;
				}
				if ($file =~ /^\Q$filename$ext\E$/) {
					$pod = $file;
				}
			}
		}
		closedir(*DIR);
		if ($localePod) {
			$pod = $localePod;
		}
		elsif ($localeLang) {
			$pod = $localeLang;
		}
	}

	# Display the
	if ($pod) {
		my $pod = File::Spec->catfile(@_, $pod);
		if ( -r "$pod" ) {
			use Pod::Perldoc;
			@ARGV = ( "$pod" );
			Pod::Perldoc->run();
			exit(0);
		}
	}
	print STDERR locGet(_T("no manual page found\n"));
	exit(255);
}

=pod

=item B<isHash($)>

Replies if the given value is a reference to a hashtable.

I<Parameters:>

=over 8

=item * a variable of scalar type.

=back

I<Returns:> C<true> if the parameter is a reference to a hashtable, otherwhise C<false>.

=cut
sub isHash($) {
	return 0 unless defined($_[0]) ;
	my $r = ref( $_[0] ) ;
	return ( $r eq "HASH" ) ;
}

=pod

=item B<isArray($)>

Replies if the given value is a reference to an array.

I<Parameters:>

=over 8

=item * a variable of scalar type.

=back

I<Returns:> C<true> if the parameter is a reference to an array, otherwhise C<false>.

=cut
sub isArray($) {
	return 0 unless defined($_[0]) ;
	my $r = ref( $_[0] ) ;
	return ( $r eq "ARRAY" ) ;
}

=pod

=item B<arrayContains(\@$)>

Replies if an element exists in an array.
The equality test is based on the C<eq> operator.

I<Parameters:>

=over 8

=item * the array in which the search must be done.

=item * the element to search for.

=back

I<Returns:> C<true> if the element is inside the array, otherwhise C<false>

=cut
sub arrayContains(\@$) {
	foreach my $e (@{$_[0]}) {
		if ($_[1] eq $e) {
			return 1;
		}
	}
	return 0;
}

=pod

=item B<arrayIndexOf(\@$)>

Replies the index of an element in the array.
The equality test is based on the C<eq> operator.

I<Parameters:>

=over 8

=item * the array in which the search must be done.

=item * the element to search for.

=back

I<Returns:> the index or C<-1> if the element was not found.

=cut
sub arrayIndexOf(\@$) {
	for(my $i=0; $i<@{$_[0]}; $i++) {
		if ($_[1] eq $_[0]->[$i]) {
			return $i;
		}
	}
	return -1;
}

=pod

=item B<removeFromArray(\@$)>

Remove all the occurences of the specified element
from an array.
The equality test is based on the C<eq> operator.

I<Parameters:>

=over 8

=item * the array.

=item * the element to remove.

=back

I<Returns:> the array in which all the elements was removed.

=cut
sub removeFromArray(\@@) {
	my @tab2 = @_;
	my $t = shift @tab2;
	my @tab = ();
	foreach my $e (@{$t}) {
		if (!arrayContains(@tab2,$e)) {
			push @tab, "$e";
		}
	}
	@{$_[0]} = @tab;
}

sub makeMessage($$@) {
	my $limit = shift;
	my $indent = shift;
	my @part = split(/\n/, join(' ',@_));
	$limit -= $indent;
	my $indentstr = '';
	while (length($indentstr)<$indent) {
		$indentstr .= ' ';
	}
	my @text = ();
	foreach my $p (@part) {
		my $splitted = undef;
		while (length("$p")>$limit) {
			push @text, ($splitted?'>':' ').$indentstr.substr("$p", 0, $limit)."[...]";
			$p = substr("$p", $limit);
			$splitted = 1;
		}
		push @text, ($splitted?'>':' ').$indentstr."$p" if ($p);
	}
	@part = undef;
	return @text;
}

=pod

=item B<setDebugLevel($)>

Set the debug level. This level is used by L<printDbg>
to know is a debug message could be displayed.

=cut
sub setDebugLevel($) {
	$debugLevel = "$_[0]";
}

=pod

=item B<getDebugLevel()>

Replies the debug level. This level is used by L<printDbg>
to know is a debug message could be displayed.

=cut
sub getDebugLevel() {
	return "$debugLevel";
}

=pod

=item B<printDbg(@)>

display a DEBUG message. The parameters will be displayed separated by a space character.

=cut
sub printDbg(@) {
	printDbgFor(1,@_);
}

=pod

=item B<printDbgIndent()>

Indent future DEBUG messages.

=cut
sub printDbgIndent() {
	$dbgIndent += 4;
	$dbgIndent = 50 if ($dbgIndent>50);
}

=pod

=item B<printDbgUnindent()>

Unindent future DEBUG messages.

=cut
sub printDbgUnindent() {
	$dbgIndent -= 4;
	$dbgIndent = 0 if ($dbgIndent<0);
}

=pod

=item B<printDbgFor($@)>

display a DEBUG message. The parameters will be displayed separated by a space character.

=cut
sub printDbgFor($@) {
	my $requestedLevel = shift;
	if ($debugLevel>=$requestedLevel) {
		my @text = makeMessage(60,$dbgIndent,@_);
		foreach my $p (@text) {
			print STDERR (_T("[AutoLaTeX]"), " $p", "\n");
		}
	}
	1;
}

=pod

=item B<dumpDbgFor($@)>

display the internal value of the specified variables.

=cut
sub dumpDbgFor($@) {
	my $requestedLevel = shift;
	if ($debugLevel>=$requestedLevel) {
		use Data::Dumper;
		my @text = makeMessage(60,$dbgIndent,Dumper(@_));
		foreach my $p (@text) {
			print STDERR (_T("[AutoLaTeX]"), " $p", "\n");
		}
	}
	1;
}

=pod

=item B<locDbg($@)>

Equivalent to printDbg(locGet(@_))

=cut
sub locDbg($@) {
	my $msgId = shift;
	printDbg(locGet($msgId, @_));
}

=pod

=item B<printErr(@)>

display an error message and exit. The parameters will be displayed separated by a space character.

=cut
sub printErr(@) {
	my @text = makeMessage(55,0,@_);
	foreach my $p (@text) {
		print STDERR (_T("[AutoLaTeX]"), ' ', locGet("Error: {}","$p"), "\n");
	}
	exit(255);
	undef;
}

=pod

=item B<printWarn(@)>

display a warning message. The parameters will be displayed separated by a space character.

=cut
sub printWarn(@) {
	my @text = makeMessage(50,0,@_);
	foreach my $p (@text) {
		print STDERR (_T("[AutoLaTeX]"), ' ', locGet(_T("Warning: {}"),"$p"), "\n");
	}
	1;
}

=pod

=item B<runCommandOrFailRedirectTo($@)>

Run a system command, block and stop the program when the
command has failed. The standartd output of the command
is written (in binary mode when possible) into the file
with the name given as first parameter.

=over 4

=item C<file> is the file in which the stdout must be written.

=item is the command to run.

=back

I<Returns:> Always C<0>.

=cut
sub runCommandOrFailRedirectTo($@) {
	my $stdoutfile = shift;
	printDbgFor(4, locGet(_T("Command line is:\n{}"), join(' ',@_)));
	my $pid = fork();
	if ($pid == 0) {
		# Child process
		open(STDOUT, '>', "$stdoutfile") or printErr(locGet(_T("Can't redirect STDOUT: {}"), $!));
		open(STDERR, '>', "autolatex_exec_stderr.log") or printErr(locGet(_T("Can't redirect STDERR: {}"), $!));
		select STDERR; $| = 1;  # make unbuffered
		select STDOUT; $| = 1;  # make unbuffered
		exec(@_);
	}
	elsif (defined($pid)) {
		# Parent process
		my $kpid = waitpid($pid, 0);
		my $exitcode = $?;
		my @stdout = ();
		if ($kpid>0) {
			local *LOGFILE;
			if ($exitcode!=0) {
				open(*LOGFILE, "< autolatex_exec_stderr.log") or printErr(locGet(_T("{}: {}"), "autolatex_exec_stderr.log", $!));
				while (my $line = <LOGFILE>) {
					print STDERR $line;
				}
				close(*LOGFILE);
			}
		}
		unlink("autolatex_exec_stdout.log");
		unlink("autolatex_exec_stderr.log");
	}
	else {
		printErr(locGet(_T("Unable to fork for the system command: {}"),join(' ',@_)));
	}
	return 0;
}

=pod

=item B<runCommandOrFail(@)>

Run a system command, block and stop the program when the
command has failed.

=over 4

=item is the command to run.

=back

I<Returns:> If this function is called in an array context, an array of all
the lines from the stdout is replied.
If this function is not called in an array context, the exit code 0 is always
replied.

=cut
sub runCommandOrFail(@) {
	printDbgFor(4, locGet(_T("Command line is:\n{}"), join(' ',@_)));
	my $wantstdout = wantarray;
	my $pid = fork();
	if ($pid == 0) {
		# Child process
		open(STDOUT, '>', "autolatex_exec_stdout.log") or printErr(locGet(_T("Can't redirect STDOUT: {}"), $!));
		open(STDERR, '>', "autolatex_exec_stderr.log") or printErr(locGet(_T("Can't redirect STDERR: {}"), $!));
		select STDERR; $| = 1;  # make unbuffered
		select STDOUT; $| = 1;  # make unbuffered
		exec(@_);
	}
	elsif (defined($pid)) {
		# Parent process
		my $kpid = waitpid($pid, 0);
		my $exitcode = $?;
		my @stdout = ();
		if ($kpid>0) {
			local *LOGFILE;
			if ($exitcode!=0) {
				open(*LOGFILE, "< autolatex_exec_stdout.log") or printErr(locGet(_T("{}: {}"), "autolatex_exec_stdout.log", $!));
				while (my $line = <LOGFILE>) {
					print STDOUT $line;
				}
				close(*LOGFILE);
				open(*LOGFILE, "< autolatex_exec_stderr.log") or printErr(locGet(_T("{}: {}"), "autolatex_exec_stderr.log", $!));
				while (my $line = <LOGFILE>) {
					print STDERR $line;
				}
				close(*LOGFILE);
				@_ = map { '\''.addSlashes($_).'\''; } @_;
				confess("\$ ", join(' ', @_));
			}
			elsif ($wantstdout) {
				@stdout = readFileLines("autolatex_exec_stdout.log");
			}
		}
		unlink("autolatex_exec_stdout.log");
		unlink("autolatex_exec_stderr.log");
		if ($wantstdout) {
			return @stdout;
		}
	}
	else {
		printErr(locGet(_T("Unable to fork for the system command: {}"),join(' ',@_)));
	}
	return 0;
}

=pod

=item B<runCommandSilently(@)>

Run a system command, block and return the exit code.
The standard outputs are catched and trashed.



Parameters are 

=over 4

=item [options] (optional hash ref), if the first parameter is an hash table, it is assumed to be
additional options to pass to this function.

=over 4

=item C<wait> is a boolean flag that is indicating if the caller must wait for the termination of the sub-process.

=back

=item rest of the parameters are constituting the command to run.

=back

I<Returns:> If this function is called in an array context, an array of all
the lines from the stdout is replied.
If this function is not called in an array context, the exit code 0 is always
replied.

=cut
sub runCommandSilently(@) {
	my $opts = {};
	if ($_[0] && isHash($_[0])) {
		$opts = shift;
	}
	printDbgFor(4, locGet(_T("Command line is:\n{}"), join(' ',@_)));
	my $pid = fork();
	if ($pid == 0) {
		# Child process
		open(STDOUT, '>', File::Spec->devnull()) or printErr(locGet(_T("Can't redirect STDOUT: {}"), $!));
		open(STDERR, '>', File::Spec->devnull()) or printErr(locGet(_T("Can't redirect STDERR: {}"), $!));
		select STDERR; $| = 1;  # make unbuffered
		select STDOUT; $| = 1;  # make unbuffered
		exec(@_);
	}
	elsif (defined($pid)) {
		# Parent process
		if (!defined($opts->{'wait'}) || $opts->{'wait'}) {
			waitpid($pid, 0);
			return $?;
		}
		else {
			# Do not wait for the child.
			return 0;
		}
	}
	else {
		printErr(locGet(_T("Unable to fork for the system command: {}"),join(' ',@_)));
		return 1;
	}
}

=pod

=item B<runSystemCommand($@)>

Run a system command and notify a listener about the terminaison.
This subroutine does not block the caller.

=over 4

=item is the listener which will be notified with a call to C<$self-E<gt>onSystemCommandTerminaison(\@$)>

=back

=cut
sub runSystemCommand($@) {
	printDbgFor(4, locGet(_T("Command line is:\n{}"), join(' ',@_)));
	my $listener = shift;
	my $pid = fork();
	if ($pid == 0) {
		# Child process
		exec(@_);
	}
	elsif (defined($pid)) {
		# Parent process
		$runningChildren{"$pid"} = { 'listener' => $listener,
					     'command' => \@_,
					   };
		return 0;
	}
	else {
		printErr(locGet(_T("Unable to fork for the system command: {}"),join(' ',@_)));
		return 1;
	}
}

=pod

=item B<notifySystemCommandListeners()>

Notifies the listeners on system commands.

=cut
sub notifySystemCommandListeners() {
	if (%runningChildren) {
		my $currenttime = time;
		if ($currenttime>=$lastListenerCheck+1) {
			$lastListenerCheck = $currenttime;
			while (my ($pid,$data) = each(%runningChildren)) {
				my $kid = waitpid($pid, WNOHANG);
				if ($kid>0) {
					delete $runningChildren{"$pid"};
					if (($data->{'listener'})&&($data->{'listener'}->can('onSystemCommandTerminaison'))) {
						$data->{'listener'}->onSystemCommandTerminaison($data->{'commmand'},$kid);
					}
				}
			}
		}
	}
}

=pod

=item B<waitForSystemCommandTerminaison()>

Wait for the termination of asynchronous commands.

=cut
sub waitForSystemCommandTerminaison() {
	if (%runningChildren) {
		locDbg(_T("Waiting for system command sub-processes"));
		printDbgIndent();
		while (my ($pid,$data) = each(%runningChildren)) {
			if ($runningChildren{"$pid"}{'command'}) {
				printDbg(@{$runningChildren{"$pid"}{'command'}});
			}
			my $kid = waitpid($pid, 0);
			delete $runningChildren{"$pid"};
		}
		printDbgUnindent();
	}
	1;
}

=pod

=item B<exitDbg(@)>

Print the content of the parameters and exit.

=cut
sub exitDbg(@) {
	confess(Dumper(@_));
}


=pod

=item B<addSlashes($)>

Protect the special characters with backslashes.

=cut
sub addSlashes($) {
	my $text = shift;
	my $term = "$text";
	$term =~ s/([\\\'\"])/\\$1/gi;
	return $term;
}

=pod

=item B<readFileLines($)>

Read a file and replies the array of the lines (if called in array context),
or all the lines inside a single string (if called in scalar context).

=cut
sub readFileLines($) {
	local *FILE;
	if (wantarray) {
		my @lines = ();
		open(*FILE, "<".$_[0]) or printErr("$_[0]: $!");
		while (my $line = <FILE>) {
			push @lines, $line;
		}
		close(*FILE);
		return @lines;
	}
	else {
		my $lines = '';
		open(*FILE, "<".$_[0]) or printErr("$_[0]: $!");
		while (my $line = <FILE>) {
			$lines .= $line;
		}
		close(*FILE);
		return $lines;
	}
}

=pod

=item B<writeFileLines($@)>

Write the lines in the array inside the specified file.

=over 4

=item I<file> is the name of the file to write.

=item the rest of the parameters are the lines to write.

=back

=cut
sub writeFileLines($@) {
	my $file = shift;
	local *FILE;
	open(*FILE, ">$file") or printErr("$file: $!");
	foreach my $l (@_) {
		confess('undefined value') unless (defined($l));
		print FILE $l;
	}
	close(*FILE);
}

=pod

=item B<removePathPrefix($$)>

Remove the given prefix from a path.

=over 4

=item I<prefix> is the path to remove.

=item  I<path> is the path from which the prefix should be removed.

=back

=cut
sub removePathPrefix($$) {
	my $prefix = shift;
	my $path = shift;
	my @dir1 = File::Spec->splitdir($prefix);
	my @dir2 = File::Spec->splitdir($path);
	while (@dir1 && @dir2 && $dir1[0] eq $dir2[0]) {
		shift @dir1;
		shift @dir2;
	}
	return File::Spec->catdir(@dir2);
}

=pod

=item B<trim($)>

Remove the trailing white spaces.

=over 4

=item I<str> the string to parse.

=back

=cut
sub trim($) {
	my $str = $_[0] || '';
	my $s = "$str";
	$s =~ s/^\s+//s;
	$s =~ s/\s+$//s;
	return $s;
}





END {
	waitForSystemCommandTerminaison();
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
