# autolatex - Config.pm
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

Config.pm - Configuration Files

=head1 DESCRIPTION

Provides a set of utilities for manipulating cofiguration files.

To use this library, type C<use AutoLaTeX::Core::Config;>.

=head1 FUNCTIONS

The provided functions are:

=over 4

=cut
package AutoLaTeX::Core::Config;

$VERSION = '9.0';
@ISA = ('Exporter');
@EXPORT = qw( &getProjectConfigFilename &getUserConfigFilename &getSystemConfigFilename
              &getSystemISTFilename &readConfiguration &readConfigFile &getUserConfigDirectory
	      &cfgBoolean &doConfigurationFileFixing &cfgToBoolean &writeConfigFile
	      &readOnlySystemConfiguration &readOnlyUserConfiguration &readOnlyProjectConfiguration
	      &setInclusionFlags &reinitInclusionFlags &cfgIsBoolean ) ;
@EXPORT_OK = qw();

use strict;
use warnings;
use vars qw(@ISA @EXPORT @EXPORT_OK $VERSION);

use File::Spec;
use Config::Simple;

use AutoLaTeX::Core::OS;
use AutoLaTeX::Core::Util;
use AutoLaTeX::Core::IntUtils;

#######################################################
# Comments for the sections of the configuration file
my %SECTION_COMMENTS = (
	'viewer'		=> _T("Configuration of the viewing functions"),
	'generation'		=> _T("Configuration of the generation functions"),
	'clean'			=> _T("Configuration of the several cleaning functions"),
	'scm'			=> _T("Configuration of the SCM functions"),
	'gtk'			=> _T("GTK interface configuration"),
	'qt'			=> _T("Qt interface configuration"),
	'windows'		=> _T("Windows interface configuration"),
	'macos'			=> _T("MacOS interface configuration"),
	'wxwidget'		=> _T("wxWidgets interface configuration"),
);

#######################################################
# Comments for the public configuration entries
my %CONFIGURATION_COMMENTS = (
	# <NO CATEGORY>
	# CLEAN
	'clean.files to clean'			=> _T(	"List of additional files to remove when cleaning (shell ".
							"wild cards are allowed). This list is used when the ".
							"target 'clean' is invoked."),
	'clean.files to desintegrate'		=> _T(	"List of additional files to remove when all cleaning ".
							"(shell wild cards are allowed). This list is used when ".
							"the target 'cleanall' is invoked."),
	# GENERATION
	'generation.biblio'			=> _T(	"Indicates if bibliography tool (bibtex,biber) should be run ('yes' or 'no')."),
	'generation.generate images'		=> _T(	"Does the figures must be automatically generated ('yes' or 'no')?"),
	'generation.image directory'		=> _T(	"Specify the directories inside which AutoLaTeX ".
							"will find the pictures which must be processed ".
							"by the translators. Each time this option is ".
							"put on the command line, a directory is added ".
							"inside the list of the directories to explore. ".
							"The different paths are separated by the ".
							"path-separator character (':' on Unix, ';' on ".
							"Windows)"),
	'generation.main file'			=> _T(	"Main filename (this option is only available in project's ".
							"configuration files)."),
	'generation.generation type'		=> _T(	"Type of generation.\n   pdf   : use pdflatex to create a ".
							"PDF document."),
	'generation.makeindex style'		=> _T(	"Specify the style that must be used by makeindex.\n".
							"Valid values are:\n   <filename>      if a filename ".
							"was specified, AutoLaTeX assumes that it is the .ist ".
							"file;\n   \@system         AutoLaTeX uses the system ".
							"default .ist file (in AutoLaTeX distribution);\n".
							"   \@detect         AutoLaTeX will tries to find a .ist ".
							"file in the project's directory. If none was found, ".
							"AutoLaTeX will not pass a style to makeindex;\n   \@none".
							"           AutoLaTeX assumes that no .ist file must be ".
							"passed to makeindex;\n   <empty>         AutoLaTeX assumes ".
							"that no .ist file must be passed to makeindex."),
	'generation.translator include path'	=> _T(	"Defines the paths from which the translators could be ".
							"loaded. This is a list of paths separated by the path ".
							"separator character used by your operating system: ':' ".
							"on Unix platforms or ';' on Windows platforms for example."),
	'generation.synctex'			=> _T(	"Indicates if the PDF document must be produced with the SyncTeX flag on or not. ".
							"SyncTeX enables to link a PDF viewer (as evince) and a text editor (as Gedit). ".
							"When you click inside one, the other is highlighting the line in its side."),
	# SCM
	'scm.scm commit'			=> _T(	"Tool to launch when a SCM commit action is requested. ".
							"Basically the SCM tools are CVS, SVN, or GIT."),
	'scm.scm update'			=> _T(	"Tool to launch when a SCM update action is requested. ".
							"Basically the SCM tools are CVS, SVN, or GIT."),
	# VIEWER
	'viewer.view' 				=> _T(	"Indicates if a viewer should be launch after the compilation. ".
							"Valid values are 'yes' and 'no'."),
	'viewer.viewer' 			=> _T(	"Specify, if not commented,the command line of the viewer."),
	'viewer.asynchronous run'		=> _T(	"Indicates if the viewer is launched in background, or not."),
);

#######################################################
# Comments for the private configuration entries
# 		action.create config file
#		action.create ist file
#		action.fix config file
#		config.command line
#		input.project directory
#		input.latex file
#		output.directory
#		ouput.ist file
#		output.latex basename


=pod

=item B<getProjectConfigFilename(@)>

Replies the name of a project's configuration file
which is located inside the given directory.

I<Parameters:>

=over 8

=item * the components of the paths, each parameter is a directory in the path.

=back

I<Returns:> the configuration filename according to the current operating system rules.

=cut
sub getProjectConfigFilename(@) {
	my $operatingsystem = getOperatingSystem();
	if (("$operatingsystem" eq 'Unix')||(("$operatingsystem" eq 'Cygwin'))) {
		return File::Spec->rel2abs(File::Spec->catfile(@_,".autolatex_project.cfg"));
	}
	else {
		return File::Spec->rel2abs(File::Spec->catfile(@_,"autolatex_project.cfg"));
	}
}

=pod

=item B<getUserConfigFilename()>

Replies the name of a user's configuration file.

I<Returns:> the configuration filename according to the current operating system rules.

=cut
sub getUserConfigFilename() {
	my $confdir = getUserConfigDirectory();
	if (-d "$confdir") {
		return File::Spec->catfile("$confdir","autolatex.conf");
	}
	my $operatingsystem = getOperatingSystem();
	if (("$operatingsystem" eq 'Unix')||(("$operatingsystem" eq 'Cygwin'))) {
		return File::Spec->rel2abs(File::Spec->catfile($ENV{'HOME'},".autolatex"));
	}
	elsif ("$operatingsystem" eq 'Win32') {
		return File::Spec->rel2abs(File::Spec->catfile("C:","Documents and Settings",$ENV{'USER'},"Local Settings","Application Data","autolatex.conf"));
	}
	else {
		return File::Spec->rel2abs(File::Spec->catfile($ENV{'HOME'},"autolatex.conf"));
	}
}

=pod

=item B<getUserConfigDirectory()>

Replies the name of a user's configuration directory.

I<Returns:> the configuration directory according to the current operating system rules.

=cut
sub getUserConfigDirectory() {
	my $operatingsystem = getOperatingSystem();
	if (("$operatingsystem" eq 'Unix')||(("$operatingsystem" eq 'Cygwin'))) {
		return File::Spec->rel2abs(File::Spec->catfile($ENV{'HOME'},".autolatex"));
	}
	elsif ("$operatingsystem" eq 'Win32') {
		return File::Spec->rel2abs(File::Spec->catfile("C:","Documents and Settings",$ENV{'USER'},"Local Settings","Application Data","autolatex"));
	}
	else {
		return File::Spec->rel2abs(File::Spec->catfile($ENV{'HOME'},"autolatex"));
	}
}

=pod

=item B<getSystemConfigFilename()>

Replies the name of the configuration file for all users.

I<Returns:> the configuration filename according to the current operating system rules.

=cut
sub getSystemConfigFilename() {
	return File::Spec->catfile(getAutoLaTeXDir(),"default.cfg");
}

=pod

=item B<getSystemISTFilename()>

Replies the name of the MakeIndex style file for all users.

I<Returns:> the filename according to the current operating system rules.

=cut
sub getSystemISTFilename() {
	return File::Spec->catfile(getAutoLaTeXDir(),"default.ist");
}

=pod

=item B<cfgBoolean($;$)>

Replies the Perl boolean value that corresponds to the specified
string. If the first parameter is not a valid boolean string, the second
parameter will be replied if it is specified; if not undef will be replied;

The valid string are (case insensitive): S<true>, S<false>, S<yes>, S<no>.

I<Parameters:>

=over 8

=item * the value to test.

=item * the data structure to fill

=back

I<Returns:> nothing

=cut
sub cfgBoolean($;$) {
	if ($_[0]) {
		my $v = lc($_[0]);
		return 1 if (($v eq 'yes')||($v eq 'true'));
		return 0 if (($v eq 'no')||($v eq 'false'));
	}
	return $_[1];
}

=pod

=item B<cfgToBoolean($)>

Replies the configuration's file boolean value that corresponds to the specified
Perl boolean value.

I<Parameters:>

=over 8

=item * the value to test.

=back

I<Returns:> nothing

=cut
sub cfgToBoolean($) {
	return ($_[0]) ? 'true' : 'false';
}

=pod

=item B<cfgIsBoolean($)>

Replies if the specified string is a valid boolean string.

I<Parameters:>

=over 8

=item * the value to test.

=back

I<Returns:> nothing

=cut
sub cfgIsBoolean($) {
	if (defined($_[0])) {
		my $v = lc($_[0]);
		return 1
			if (($v eq 'yes')||($v eq 'no')||($v eq 'true')||($v eq 'false'));
	}
	return 0;
}

=pod

=item B<readConfiguration()>

Replies the current configuration. The configuration
is extracted from the system configuration file
(from AutoLaTeX distribution) and from the user
configuration file.

I<Returns:> a hashtable containing (attribute name, attribute value) pairs.
The attribute name could be S<section.attribute> to describe the attribute inside
a section.

=cut
sub readConfiguration() {
	my %configuration = ();
	my $systemFile = getSystemConfigFilename();
	my $userFile = getUserConfigFilename();
	readConfigFile("$systemFile",\%configuration);
	readConfigFile("$userFile",\%configuration);
	# Remove the main intput filename
	if (exists $configuration{'generation.main file'}) {
		delete $configuration{'generation.main file'};
	}
	return %configuration;
}

=pod

=item B<readOnlySystemConfiguration()>

Replies the current configuration. The configuration
is extracted from the system configuration file
(from AutoLaTeX distribution) only.

I<Returns:> a hashtable containing (attribute name, attribute value) pairs.
The attribute name could be S<section.attribute> to describe the attribute inside
a section.

=cut
sub readOnlySystemConfiguration(;$) {
	my %configuration = ();
	my $systemFile = getSystemConfigFilename();
	readConfigFile("$systemFile",\%configuration,$_[0]);
	# Remove the main intput filename
	if (exists $configuration{'generation.main file'}) {
		delete $configuration{'generation.main file'};
	}
	return %configuration;
}

=pod

=item B<readOnlyUserConfiguration(;$)>

Replies the current configuration. The configuration
is extracted from the user configuration file
($HOME/.autolatex or $HOME/.autolatex/autolatex.conf) only.

I<Returns:> a hashtable containing (attribute name, attribute value) pairs.
The attribute name could be S<section.attribute> to describe the attribute inside
a section.

=cut
sub readOnlyUserConfiguration(;$) {
	my %configuration = ();
	my $userFile = getUserConfigFilename();
	readConfigFile("$userFile",\%configuration,$_[0]);
	# Remove the main intput filename
	if (exists $configuration{'generation.main file'}) {
		delete $configuration{'generation.main file'};
	}
	return %configuration;
}

=pod

=item B<readOnlyProjectConfiguration(@)>

Replies the current configuration. The configuration
is extracted from the project configuration file
($PROJECT_PATH/.autolatex_project.cfg) only.

I<Returns:> a hashtable containing (attribute name, attribute value) pairs.
The attribute name could be S<section.attribute> to describe the attribute inside
a section.

=cut
sub readOnlyProjectConfiguration(@) {
	my %configuration = ();
	my $userFile = getProjectConfigFilename(@_);
	if (-r "$userFile") {
		readConfigFile("$userFile",\%configuration);
		$configuration{'__private__'}{'input.project directory'} = File::Spec->catfile(@_);
		return \%configuration;
	}
	return undef;
}

=pod

=item B<readConfigFile($\%;$)>

Fill the configuration data structure from the specified file information.
The structure of the filled hashtable is a set of (attribute name, attribute value) pairs.
The attribute name could be S<section.attribute> to describe the attribute inside
a section.

I<Parameters:>

=over 8

=item * the name of the file to read

=item * the data structure to fill

=item * boolean value that indicates if a warning message should be ignored when an old fashion file was detected.

=back

I<Returns:> nothing

=cut
sub readConfigFile($\%;$) {
	my $filename = shift;
	die('second parameter of readConfigFile() is not a hash') unless(isHash($_[0]));
	printDbg(formatText(_T("Opening configuration file {}"),$filename));
	if (-r "$filename") {
		my $cfgReader = new Config::Simple("$filename");
		my %config = $cfgReader->vars();
		my $warningDisplayed = $_[1];
		while (my ($k,$v) = each (%config)) {
			$k = lc("$k");
			if ($k !~ /^__private__/) {
				($k,$v) = ensureAccendentCompatibility("$k",$v,"$filename",$warningDisplayed);
				$_[0]->{"$k"} = rebuiltConfigValue("$k",$v);
			}
		}
		printDbg(_T("Succeed on reading"));
	}
	else {
		printDbg(formatText(_T("Failed to read {}: {}"),$filename,$!));
	}
	1;
}

# Put formatted comments inside an array
sub pushComment(\@$;$) {
	my $limit = $_[2] || 60;
	$limit = 1 unless ($limit>=1);
	my @lines = split(/\n/, $_[1]);
	foreach my $line (@lines) {
		my @words = split(/\s+/, $line);
		my $wline = '';
		if ($line =~ /^(\s+)/) {
			$wline .= $1;
		}
		foreach my $w (@words) {
			if ((length($wline)+length($w)+1)>$limit) {
				push @{$_[0]}, "#$wline\n";
				if (length($w)>$limit) {
					while (length($w)>$limit) {
						push @{$_[0]}, "# ".substr($w,0,$limit)."\n";
						$w = substr($w,$limit);
					}
				}
				$wline = " $w";
			}
			else {
				$wline .= " $w";
			}
		}
		if ($wline) {
			push @{$_[0]}, "#$wline\n";
		}
	}
}

=pod

=item B<writeConfigFile($\%)>

Write the specified configuration into a file.

I<Parameters:>

=over 8

=item * the name of the file to write

=item * the configuration data structure to write

=back

I<Returns:> nothing

=cut
sub writeConfigFile($\%) {
	my $filename = shift;
	die('second parameter of writeConfigGile() is not a hash') unless(isHash($_[0]));

	# Write the values
	printDbg(formatText(_T("Writing configuration file {}"),$filename));
	printDbgIndent();
	my $cfgWriter = new Config::Simple(syntax=>'ini');
	while (my ($attr,$value) = each (%{$_[0]})) {
		if ($attr ne '__private__') {
			$cfgWriter->param("$attr",$value);
		}
	}
	$cfgWriter->write("$filename");

	# Updating for comments
	printDbg(_T("Adding configuration comments"));
	local *CFGFILE;
	open (*CFGFILE, "< $filename") or printErr("$filename:","$!");
	my @lines = ();
	my $lastsection = undef;
	while (my $l = <CFGFILE>) {
		if ($l =~ /^\s*\[\s*(.+?)\s*\]\s*$/) {
			$lastsection = lc($1);
			if ($SECTION_COMMENTS{"$lastsection"}) {
				push @lines, "\n";
				pushComment @lines, $SECTION_COMMENTS{"$lastsection"};
			}
			else {
				push @lines, "\n";
				pushComment @lines, _T("Configuration of the translator")." '$lastsection'";
			}
		}
		elsif (($l =~ /^\s*(.*?)\s*=/)&&($lastsection)) {
			my $attr = lc($1);
			if ($CONFIGURATION_COMMENTS{"$lastsection.$attr"}) {
				push @lines, "\n";
				pushComment @lines, $CONFIGURATION_COMMENTS{"$lastsection.$attr"};
			}
		}
		push @lines, $l;
	}
	close(*CFGFILE);

	printDbg(_T("Saving configuration comments"));
	local *CFGFILE;
	open (*CFGFILE, "> $filename") or printErr("$filename:","$!");
	print CFGFILE (@lines);
	close(*CFGFILE);	

	printDbgUnindent();
	1;
}

=pod

=item B<doConfigurationFileFixing($)>

Fix the specified configuration file.

I<Parameters:>

=over 8

=item * the name of the file to fix

=back

I<Returns:> nothing

=cut
sub doConfigurationFileFixing($) {
	my $filename = shift;
	my %configuration = ();

	readConfigFile("$filename",%configuration,1);

	writeConfigFile("$filename",%configuration);

	1;
}

# Try to detect an old fashioned configuration file
# and fix the value
sub ensureAccendentCompatibility($$$$) {
	my $k = $_[0];
	my $v = $_[1];
	my $changed = 0;
	$v = '' unless (defined($v));

	if ($k eq 'generation.bibtex') {
		$k = 'generation.biblio';
		$changed = 1;
	}

	if (!isArray($v)) {
		# Remove comments on the same line as values
		if ($v =~ /^\s*(.*?)\s*\#.*$/) {
			$v = "$1" ;
			$changed = 1;
		}

		if ($v eq '@detect@system') {
			$v = ['detect','system'];
			$changed = 1;
		}
	}

	if (($changed)&&(!$_[3])) {
		printWarn(formatText(_T("AutoLaTeX has detecting an old fashion syntax for the configuration file {}\nPlease regenerate this file with the command line option --fixconfig."), $_[2]));
		$_[3] = 1;
	}

	return ($k,$v);
}

# Reformat the value from a configuration file to apply several rules
# which could not be directly applied by the configuration readed.
# $_[0]: value name,
# $_[1]: value to validated.
sub rebuiltConfigValue($$) {
	my $v = $_[1];
	if (($_[0])&&($v)) {
		if ($_[0] eq 'generation.translator include path') {
			my $sep = getPathListSeparator();
			if (isHash($v)) {
				while (my ($key,$val) = each(%{$v})) {
					my @tab = split(/\s*$sep\s*/,"$val");
					if (@tab>1) {
						$v->{"$key"} = @tab;
					}
					else {
						$v->{"$key"} = pop @tab;
					}
				}
			}
			else {
				my @paths = ();
				if (isArray($v)) {
					foreach my $p (@{$v}) {
						push @paths, split(/\s*$sep\s*/,"$p");
					}
				}
				else {
					push @paths, split(/\s*$sep\s*/,"$v");
				}
				if (@paths>1) {
					$v = \@paths;
				}
				else {
					$v = pop @paths;
				}
			}
		}
	}
	return $v;
}

=pod

=item B<setInclusionFlags(\%\%;\%\%)>

Set the translator inclusion flags obtained from the configurations.

This function assumed that the translator list is an hashtable of
(translator_name => { 'included' => { level => boolean } }) pairs.

I<Parameters:>

=over 8

=item * the translator list.

=item * the system configuration.

=item * the user configuration.

=item * the project configuration.

=back

I<Returns:> nothing

=cut
sub setInclusionFlags(\%\%;\%\%) {
	die('first parameter of setInclusionFlags() is not a hash')
		unless (isHash($_[0]));
	die('second parameter of setInclusionFlags() is not a hash')
		unless (isHash($_[1]));
	foreach my $trans (keys %{$_[0]}) {
		if (!$_[0]->{"$trans"}{'included'}) {
			$_[0]->{"$trans"}{'included'} = {};
		}

		if ((exists $_[1]->{"$trans.include module"})&&(cfgIsBoolean($_[1]->{"$trans.include module"}))) {
			$_[0]->{"$trans"}{'included'}{'system'} = cfgBoolean($_[1]->{"$trans.include module"});
		}
		else {
			# On system level, a module which was not specified as not includable must
			# be included even if it will cause conflicts
			$_[0]->{"$trans"}{'included'}{'system'} = undef;
		}

		if (($_[2])&&
		    (exists $_[2]->{"$trans.include module"})&&
		    (cfgIsBoolean($_[2]->{"$trans.include module"}))) {
			$_[0]->{"$trans"}{'included'}{'user'} = cfgBoolean($_[2]->{"$trans.include module"});
		}
		else {
			$_[0]->{"$trans"}{'included'}{'user'} = undef;
		}

		if (($_[3])&&
		    (exists $_[3]->{"$trans.include module"})&&
		    (cfgIsBoolean($_[3]->{"$trans.include module"}))) {
			$_[0]->{"$trans"}{'included'}{'project'} = cfgBoolean($_[3]->{"$trans.include module"});
		}
		else {
			$_[0]->{"$trans"}{'included'}{'project'} = undef;
		}
	}
}

=pod

=item B<reinitInclusionFlags(\%\%;\%\%)>

Init the translator inclusion flags obtained from the configurations.

This function assumed that the translator list is an hashtable of
(translator_name => { 'included' => { level => undef } }) pairs.

I<Parameters:>

=over 8

=item * the translator list.

=item * the system configuration.

=item * the user configuration.

=item * the project configuration.

=back

I<Returns:> nothing

=cut
sub reinitInclusionFlags(\%\%;\%\%) {
	die('first parameter of setInclusionFlags() is not a hash')
		unless (isHash($_[0]));
	die('second parameter of setInclusionFlags() is not a hash')
		unless (isHash($_[1]));
	foreach my $trans (keys %{$_[0]}) {
		if (!$_[0]->{"$trans"}{'included'}) {
			$_[0]->{"$trans"}{'included'} = {};
		}

		$_[0]->{"$trans"}{'included'}{'system'} = undef;

		if ($_[2]) {
		    $_[0]->{"$trans"}{'included'}{'user'} = undef;
		}

		if ($_[3]) {
			$_[0]->{"$trans"}{'included'}{'project'} = undef;
		}
	}
}

1;
__END__
=back

=head1 BUG REPORT AND FEEDBACK

To report bugs, provide feedback, suggest new features, etc. (in prefered order): a) visit the developer site on GitHub <https://github.com/gallandarakhneorg/autolatex/>, b) visit the AutoLaTeX main page <http://www.arakhne.org/autolatex/>, or c) send email to the main author at galland@arakhne.org.

=head1 LICENSE

S<GNU Public License (GPL)>

=head1 COPYRIGHT

S<Copyright (c) 1998-13 Stéphane Galland E<lt>galland@arakhne.orgE<gt>>

=head1 SEE ALSO

L<autolatex-dev>
