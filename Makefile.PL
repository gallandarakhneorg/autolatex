#!/usr/bin/perl -W

use strict;
use Getopt::Long;
use File::Basename;
use File::Spec;
use File::Copy;
use Compress::Zlib;
use Pod::Text;
use Pod::Man;
use Pod::Html;

my %MODULES = ( 'core' => 1 , 'sty' => 1, 'gedit' => 1 );

# GENERAL INSTALLATION INFORMATIONS
my $ALLOW_SYMBOLIC_LINK;
my $INSTALLDIRECTORY;
my $BINDIRECTORY;
my $ETCDIRECTORY;
my $MANDIRECTORY;
my $LOCALEDIRECTORY;
my $ICONDIRECTORY;
my $STYDIRECTORY;
my $GEDITPLUGINDIRECTORY;
my $GSETTINGSSCHEMADIRECTORY;

sub dbg(@) {
	use Data::Dumper;
	die(Dumper(@_));
}

#------------------------------------------------------------------------------------------
sub isArray($) {
	return 0 unless defined($_[0]) ;
	my $r = ref( $_[0] ) ;
	return ( $r eq "ARRAY" ) ;
}

#------------------------------------------------------------------------------------------
sub arrayContains(\@$) {
	if (!$_[0]) {
		return 0;
	}
	foreach my $e (@{$_[0]}) {
		if ($_[1] eq $e) {
			return 1;
		}
	}
	return 0;
}

#------------------------------------------------------------------------------------------
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

#------------------------------------------------------------------------------------------
sub substShellPatterns($) {
	my $t = '';
	$t = "$_[0]" if ($_[0]);
	if ($t) {
		$_[0] =~ s/^~([a-z_0-9]+)/
			my @l = getpwnam("$1");
			if (@l>=8) {
				"$l[7]";
			}
			else {
				"~$1";
			}
			/e;
		$_[0] =~ s/^~\//$ENV{'HOME'}\//;
	}
	return $_[0];
}

#------------------------------------------------------------------------------------------
sub gzipfct($) {
	my $targetfile = shift;
	local *IN;
	my $gz = gzopen("$targetfile.gz","wb") or die("$targetfile.gz: $!");
	open(*IN, "<", "$targetfile") or die("$targetfile: $!");
	while (<IN>) {
		$gz->gzwrite($_);
	}
	close(*IN);
	$gz->gzclose();
	unlink "$targetfile";
}

#------------------------------------------------------------------------------------------
sub rm($) {
	my $delfile = shift;
	if (-f "$delfile") {
		print "delete $delfile\n";
		unlink "$delfile";
	}
}

#------------------------------------------------------------------------------------------
sub getFilesRec($$@) {
	my $exceptions = shift || [];
	my $directory = shift;
	my $pattern = shift;
	my @list = ();
	if (($pattern)&&(-d "$directory")) {
		# Make a pattern
		$pattern =~ s/\./\\./g;
		$pattern =~ s/\*/.*/g;

		# Get the directory content
		my @subdirs = ();
		local *DIR;
		opendir(*DIR,"$directory")
			or die("$directory: $!\n");
		while (my $d = readdir(*DIR)) {
			if (($d ne File::Spec->curdir())&&($d ne File::Spec->updir())&&
			    ($d =~ /^$pattern$/) &&
			    (!arrayContains(@{$exceptions}, "$d"))) {
				my $full = File::Spec->catfile($directory,$d);
				if (-d "$full") {
					push @subdirs, "$full";
				}
				elsif (!@_) {
					push @list, "$full";
				}
			}
		}
		closedir(*DIR);

		# Go into sub directories
		foreach my $d (@subdirs) {
			my @l = &getFilesRec($exceptions,"$d",@_);
			push @list, @l;
		}
	}
	return @list;
}
sub getFiles(@) {
	my $firstpart = shift;
	my $exceptions;
	if (isArray($firstpart)) {
		$exceptions = $firstpart;
		$firstpart = shift;
	}
	else {
		$exceptions = [];
	}
	if ($firstpart) {
		return getFilesRec($exceptions, '.',$firstpart,@_);
	}
	else {
		return getFilesRec($exceptions, FileSpec->rootdir(),@_);
	}
}

#------------------------------------------------------------------------------------------
sub getDirectories(@) {
	my @list;
	local *DIR;
	foreach my $d (@_) {
		if (-d "$d") {
			opendir(*DIR,"$d") or die("$d: $!\n");
			while (my $sd = readdir(*DIR)) {
				if (($sd ne File::Spec->curdir())&&($sd ne File::Spec->updir())) {
					my $full = File::Spec->catfile($d,$sd);
					if (-d "$full") {
						push @list, "$full";
					}
				}
			}			
			closedir(*DIR);
		}
	}
	return @list;
}

#------------------------------------------------------------------------------------------
sub getDirectoryBasenames(@) {
	my @list;
	local *DIR;
	foreach my $d (@_) {
		if (-d "$d") {
			opendir(*DIR,"$d") or die("$d: $!\n");
			while (my $sd = readdir(*DIR)) {
				if (($sd ne File::Spec->curdir())&&($sd ne File::Spec->updir())) {
					my $full = File::Spec->catfile($d,$sd);
					if (-d "$full") {
						push @list, "$sd";
					}
				}
			}			
			closedir(*DIR);
		}
	}
	return @list;
}

#------------------------------------------------------------------------------------------
sub mkdirrec(@) {
	foreach my $dir (@_) {
		my @parts = File::Spec->splitdir($dir);
		my @np = ();
		foreach my $d (@parts) {
			if ($d) {
				my $rep = @np ? File::Spec->catdir(@np,$d) : $d;
				unless (-d "$rep") {
					mkdir("$rep") or die("$rep: $!\n");
					chmod 0755, "$rep";
				}
			}
			push @np, $d;
		}		
	}
}

#------------------------------------------------------------------------------------------
sub install($$;$) {
	my $sourcefile = shift;
	my $targetdir = shift;
	my $newbasename = shift || basename("$sourcefile");
	mkdirrec($targetdir);
	print "installing $sourcefile into $targetdir\n";
	my $fullname = File::Spec->catfile($targetdir,$newbasename);
	copy("$sourcefile","$fullname")
		or die("$sourcefile: $!\n");
	chmod 0644, "$fullname";	
	return $fullname;
}

#------------------------------------------------------------------------------------------
sub installLink($$;$) {
	return '' unless ($ALLOW_SYMBOLIC_LINK);
	my $sourcefile = File::Spec->rel2abs(shift);
	my $targetdir = File::Spec->rel2abs(shift);
	my $newbasename = shift || basename("$sourcefile");
	mkdirrec($targetdir);
	print "installing link $sourcefile into $targetdir\n";
	my $fullname = File::Spec->catfile($targetdir,$newbasename);
	my $linkname = File::Spec->abs2rel("$sourcefile","$targetdir");
	unlink("$fullname") if (-e "$fullname");
	symlink("$linkname","$fullname")
		or die("$sourcefile: $!\n");
	return $fullname;
}

#------------------------------------------------------------------------------------------
sub installExec($$;$) {
	my $fullname = install($_[0],$_[1],$_[2]);
	chmod 0755, "$fullname";	
	return $fullname;
}

#------------------------------------------------------------------------------------------
sub installCfg($;$) {
	return install($_[0],$ETCDIRECTORY,$_[1]);
}

#------------------------------------------------------------------------------------------
sub installBin($;$) {
	return installExec($_[0],$BINDIRECTORY,$_[1]);
}

#------------------------------------------------------------------------------------------
sub installLinkedBin($$;$) {
	my $fullname = installExec($_[0],$_[1]);
	my $linkname = installLink($fullname,$BINDIRECTORY,$_[2]);
	return ($fullname,$linkname);
}

#------------------------------------------------------------------------------------------
sub installMan(@) {
	my @result = ();
	my %mandirectories = ();
	foreach my $man (@_) {
		my @parts = File::Spec->splitdir($man);
		my @files = getFiles(@parts);
		die("$man: no manual file found\n") unless (@files);
		foreach my $f (@files) {
			my $base = basename($f);
			if ($base =~ /^(.*?)\.([a-z_]+)\.([0-9]+\.gz)$/) {
				my $lang = "$2";
				my $name = "$1.$3";
				unless ($mandirectories{"$lang"}) {
					my @l = File::Spec->splitdir($MANDIRECTORY);
					my $last = pop @l;
					push @l, $lang;
					push @l, $last;
					$mandirectories{"$lang"} = File::Spec->catfile(@l);
				}
				install($f,$mandirectories{"$lang"},$name);
			}
			else {
				push @result, install($f,$MANDIRECTORY);
			}
		}
	}
	return @result;
}

#------------------------------------------------------------------------------------------
sub installInto($@) {
	my $target = shift;
	my @result = ();
	foreach my $fileToInstall (@_) {
		push @result, install($fileToInstall, $target);
	}
	return @result;
}

#------------------------------------------------------------------------------------------
sub installExecInto($@) {
	my $target = shift;
	my @files = installInto($target,@_);
	foreach my $file (@files) {
		chmod 0755, "$file";
	}
	return @files;
}

#------------------------------------------------------------------------------------------
sub DO_compile(\%) {
	print "DO AUTOLATEX COMPILATION...\n";

	local *DIR;
	local *DIR2;

	my $podDirectory = File::Spec->catfile($_[0]->{'directory'},'pod');
	my $poDirectory = File::Spec->catfile($_[0]->{'directory'},'po');

	# Generate the READMEs
	my $text_parser = Pod::Text->new('sentence'=>0, 'utf8'=>1);

	opendir(*DIR, "$podDirectory") or die("$podDirectory: $!\n");
	while (my $file = readdir(*DIR)) {
		if ($file =~ /^autolatex(?:_([^.]+))?\.pod$/) {
			my $loc = $1 || '';
			my $targetFile = "README";
			$targetFile .= '_'.uc($loc) if ($loc);
			print "Generating $targetFile...\n";
			$text_parser->parse_from_file(
				File::Spec->catfile("$podDirectory","$file"),
				File::Spec->catfile($_[0]->{'directory'},"$targetFile"));
		}
	}
	closedir(*DIR);

	# Generate the manuals
	my $man_parser = Pod::Man->new('release'=>$_[0]->{'version'}, section => 1);

	opendir(*DIR, "$podDirectory") or die("$podDirectory: $!\n");
	while (my $file = readdir(*DIR)) {
		if ($file =~ /^autolatex(?:_([^.]+))?\.pod$/) {
			my $loc = $1 || '';
			my $targetFile = "autolatex";
			$targetFile .= '.'.lc($loc) if ($loc);
			$targetFile .= '.1';
			print "Generating $targetFile...\n";
			$text_parser->parse_from_file(
				File::Spec->catfile("$podDirectory","$file"),
				File::Spec->catfile("$podDirectory","$targetFile"));
			gzipfct(File::Spec->catfile("$podDirectory","$targetFile"));
		}
	}
	closedir(*DIR);

	# Generate the program translations
	opendir(*DIR,"$poDirectory") or die("$poDirectory: $!\n");
	while (my $topdir = readdir(*DIR)) {
		if (($topdir ne File::Spec->curdir())&&($topdir ne File::Spec->updir())) {
			my $subdirectory = File::Spec->catdir($poDirectory,$topdir,'LC_MESSAGES');
			opendir(*DIR2,"$subdirectory") or next;
			while (my $pofile = readdir(*DIR2)) {
				if ($pofile =~ /\.po$/i) {
					print "Generating translations for $pofile...\n";
					my $mofile = $pofile;
					$mofile =~ s/\.po/.mo/i;
					system('msgfmt','-v','-o',
						File::Spec->catfile("$subdirectory","$mofile"),
						File::Spec->catfile("$subdirectory","$pofile"));
				}
			}
			closedir(*DIR2);
		}
	}
	closedir(*DIR);
}

#------------------------------------------------------------------------------------------
sub DO_install(\%) {
	print "DO AUTOLATEX INSTALLATION...\n";
	my @po_directories = getDirectoryBasenames('po');
	if ($MODULES{'core'}) {
		if (($_[0]->{'create-links'})&&($_[0]->{'create-bin-links'})) {
			installLinkedBin('autolatex.pl', $INSTALLDIRECTORY,'autolatex');
			installLinkedBin('autolatex-gtk.pl',$INSTALLDIRECTORY,'autolatex-gtk');
			installLinkedBin('autolatex-backend.pl',$INSTALLDIRECTORY,'autolatex-backend');
		}
		else {
			installExec('autolatex.pl', $INSTALLDIRECTORY);
			installExec('autolatex-gtk.pl',$INSTALLDIRECTORY);
			installExec('autolatex-backend.pl',$INSTALLDIRECTORY);
		}
		install('AUTHORS', $INSTALLDIRECTORY);
		install('VERSION', $INSTALLDIRECTORY);
		if (($_[0]->{'create-links'})&&($_[0]->{'create-etc-links'})) {
			my $cfgFile = installCfg('default.ist');
			installLink($cfgFile,$INSTALLDIRECTORY);
			$cfgFile = installCfg('default.cfg','config');
			installLink($cfgFile,$INSTALLDIRECTORY,'default.cfg');
		}
		else {
			install('default.ist',$INSTALLDIRECTORY);
			install('default.cfg',$INSTALLDIRECTORY);
		}

		installInto(
			File::Spec->catfile($INSTALLDIRECTORY,'translators'),
			getFiles('translators','*'));

		installInto(
			File::Spec->catfile($INSTALLDIRECTORY,'pm','AutoLaTeX', 'Core'),
			getFiles('pm','AutoLaTeX','Core','*.pm'));

		installInto(
			File::Spec->catfile($INSTALLDIRECTORY,'pm','AutoLaTeX', 'Make'),
			getFiles('pm','AutoLaTeX','Make','*.pm'));

		installInto(
			File::Spec->catfile($INSTALLDIRECTORY,'pm','AutoLaTeX', 'TeX'),
			getFiles('pm','AutoLaTeX','TeX','*.pm'));

		installInto(
			File::Spec->catfile($INSTALLDIRECTORY,'pm','AutoLaTeX','GUI'),
			getFiles('pm','AutoLaTeX','GUI','*.pm'));

		installInto(
			File::Spec->catfile($INSTALLDIRECTORY,'pm','AutoLaTeX','GUI'),
			getFiles('pm','AutoLaTeX','GUI','*.png'));

		installInto(
			File::Spec->catfile($INSTALLDIRECTORY,'pm','AutoLaTeX','GUI','Gtk'),
			getFiles('pm','AutoLaTeX','GUI','Gtk','*.pm'));

		my @po_exceptions = ('geditautolatex.mo');
		foreach my $lang (@po_directories) {
			my @files = getFiles(\@po_exceptions, 'po',"$lang",'LC_MESSAGES','*.mo');
			installInto(
				File::Spec->catfile($INSTALLDIRECTORY,'po',"$lang",'LC_MESSAGES'),
				@files);
		}

		installInto(
			File::Spec->catfile($INSTALLDIRECTORY,'pod'),
			getFiles('pod','*.pod'));

		installMan('pod/autolatex.1.gz');
		installMan('pod/autolatex.fr.1.gz');
	}

	if ($MODULES{'sty'}) {
		installInto(
			$STYDIRECTORY,
			getFiles('sty','*'));
	}
	
	if ($MODULES{'gedit'}) {
		installInto(
			$GEDITPLUGINDIRECTORY,
			getFiles('plugins', 'gedit','*'));

		installInto(
			File::Spec->catfile($GEDITPLUGINDIRECTORY,'autolatex'),
			getFiles('plugins', 'gedit','autolatex','*'));

		installInto(
			File::Spec->catfile($GEDITPLUGINDIRECTORY,'autolatex','icons','24'),
			getFiles('plugins', 'gedit','autolatex','icons','24','*'));

		installInto(
			File::Spec->catfile($GEDITPLUGINDIRECTORY,'autolatex','icons','16'),
			getFiles('plugins', 'gedit','autolatex','icons','16','*'));

		installInto(
			$GSETTINGSSCHEMADIRECTORY,
			getFiles('schemas', '*.gschema.xml'));

		installInto(
			$GSETTINGSSCHEMADIRECTORY,
			getFiles('schemas', '*.gschema.xml'));

		foreach my $lang (@po_directories) {
			install(
				File::Spec->catfile('po',"$lang",'LC_MESSAGES','geditautolatex.mo'),
				File::Spec->catfile($LOCALEDIRECTORY,"$lang",'LC_MESSAGES'));
		}

		install(
			'autolatex-icon.png',
			$ICONDIRECTORY);
	}
}

#------------------------------------------------------------------------------------------
sub DO_clean(\%) {
	print "DO AUTOLATEX CLEANING...\n";
	#rm(File::Spec->catfile($_[0]->{'directory'},'README'));
	rm(File::Spec->catfile($_[0]->{'directory'},'README_FR'));
	rm(File::Spec->catfile($_[0]->{'directory'},'pod','autolatex.1.gz'));
	rm(File::Spec->catfile($_[0]->{'directory'},'pod','autolatex.fr.1.gz'));

	local *DIR;
	local *DIR2;
	my $directory = File::Spec->catdir($_[0]->{'directory'},'po');
	opendir(*DIR,"$directory") or die("$directory: $!\n");
	while (my $topdir = readdir(*DIR)) {
		if (($topdir ne File::Spec->curdir())&&($topdir ne File::Spec->updir())) {
			my $subdirectory = File::Spec->catdir($directory,$topdir,'LC_MESSAGES');
			opendir(*DIR2,"$subdirectory") or next;
			while (my $mofile = readdir(*DIR2)) {
				if ($mofile =~ /\.mo$/i) {
					rm(File::Spec->catfile("$subdirectory","$mofile"));
				}
			}
			closedir(*DIR2);
		}
	}
	closedir(*DIR);

	rm(File::Spec->catfile($_[0]->{'directory'},'Makefile'));
}

#------------------------------------------------------------------------------------------
sub DO_createMakefile(\%) {
	print "CREATING MAKEFILE...\n";
	local *OUT;

	my @options = ();
	if ($_[0]->{'version'}) {
		push @options, '"--version='.$_[0]->{'version'}.'"';
	}
	if ($_[0]->{'prefix'}) {
		push @options, '"--prefix='.$_[0]->{'prefix'}.'"';
	}
	if ($_[0]->{'man-prefix'}) {
		push @options, '"--manprefix='.$_[0]->{'man-prefix'}.'"';
	}
	if ($_[0]->{'etc-prefix'}) {
		push @options, '"--etcprefix='.$_[0]->{'etc-prefix'}.'"';
	}
	if ($_[0]->{'tex-prefix'}) {
		push @options, '"--texprefix='.$_[0]->{'tex-prefix'}.'"';
	}
	if ($_[0]->{'create-links'}) {
		push @options, '"--link"';
	}
	else {
		push @options, '"--nolink"';
	}
	if ($_[0]->{'create-etc-links'}) {
		push @options, '"--etclink"';
	}
	else {
		push @options, '"--noetclink"';
	}
	if ($_[0]->{'create-bin-links'}) {
		push @options, '"--binlink"';
	}
	else {
		push @options, '"--nobinlink"';
	}

	while (my ($module,$enable) = each(%MODULES)) {
		if ($enable) {
			push @options, "\"--enable=$module\"";
		}
		else {
			push @options, "\"--disable=$module\"";
		}
	}

	my $options = join(' ',@options);

	my $filename = File::Spec->catfile($_[0]->{'directory'},"Makefile");
	open(*OUT, "> $filename") or die("$filename: $!\n");
	print OUT "all:\n";
	print OUT "\t@ perl ".__FILE__." $options compile\n\n";
	print OUT "install:\n";
	print OUT "\t@ perl ".__FILE__." $options install\n\n";
	print OUT "clean:\n";
	print OUT "\t@ perl ".__FILE__." $options clean\n\n";
	close(*OUT);
}

#------------------------------------------------------------------------------------------
my %options = ();
$options{'directory'} = File::Spec->rel2abs(dirname(__FILE__));
$options{'create-links'} = 1;
$options{'create-bin-links'} = 1;
$options{'create-etc-links'} = 1;

# Detect the version number
local *FILE;
open(*FILE,"<".File::Spec->catfile($options{'directory'},'VERSION'))
	or die(File::Spec->catfile($options{'directory'},'VERSION').":$!\n");
while (my $line = <FILE>) {
	if ($line =~ /^\s*autolatex\s*([0-9\-a-z\.]+)\s*$/i) {
		$options{'version'} = "$1";
	}
}
close(*FILE);

# Read command line
if (!GetOptions(
		'texprefix=s' => \$options{'tex-prefix'},
		'etcprefix=s' => \$options{'etc-prefix'},
		'manprefix=s' => \$options{'man-prefix'},
		'prefix=s' => \$options{'prefix'},
		'version=s' => \$options{'version'},
		'link!' => \$options{'create-links'},
		'binlink!' => \$options{'create-bin-links'},
		'etclink!' => \$options{'create-etc-links'},
		'enable=s' => sub { if (exists $MODULES{$_[1]}) { $MODULES{$_[1]} = 1; } },
		'disable=s' => sub { if (exists $MODULES{$_[1]}) { $MODULES{$_[1]} = 0; } },
		'modules' => sub {
					foreach my $module (keys %MODULES) {
						print STDOUT "$module\n";
					}
					exit(255);
				},
		)) {
	exit(1);
}

# Detect action
$options{'action'} = 'unknow';
foreach my $act (@ARGV) {
	if ($act eq 'compile') {
		$options{'action'} = 'compile';
	}
	elsif ($act eq 'install') {
		$options{'action'} = 'install';
	}
	elsif ($act eq 'clean') {
		$options{'action'} = 'clean';
	}
}

# Set the paths
if (("$^O" eq 'MSWin32')||
    ("$^O" eq 'NetWare')||
    ("$^O" eq 'symbian')) {
	# Win32 compatible platform
	$ALLOW_SYMBOLIC_LINK = 0;

	my $PREFIX = substShellPatterns($options{'prefix'}) || File::Spec->catfile('C:','Program Files');
	my $ETCPREFIX = "$PREFIX";
	my $MANPREFIX = substShellPatterns($options{'man-prefix'}) || File::Spec->catfile('C:','Documents and Settings','All Users','Application Data');
	my $TEXPREFIX = substShellPatterns($options{'tex-prefix'}) || File::Spec->catfile($PREFIX,'autolatex','sty');

	$INSTALLDIRECTORY = File::Spec->catfile("$PREFIX",'autolatex');
	$BINDIRECTORY = File::Spec->catfile("$PREFIX",'autolatex');
	$ETCDIRECTORY = File::Spec->catfile("$ETCPREFIX",'autolatex');
	$MANDIRECTORY = File::Spec->catfile("$MANPREFIX",'autolatex','man','english');
	$LOCALEDIRECTORY = File::Spec->catfile("$PREFIX",'autolatex', 'locale');
	$ICONDIRECTORY = File::Spec->catfile("$PREFIX",'autolatex', 'icons');
	$STYDIRECTORY = File::Spec->catfile("$TEXPREFIX",'tex','latex','autolatex');
	$GEDITPLUGINDIRECTORY = File::Spec->catfile("$PREFIX",'gedit','plugins','autolatex');
	$GSETTINGSSCHEMADIRECTORY = File::Spec->catfile("$PREFIX",'glib-2.0','schemas');
}
else {
	# Unix compatible platform
	$ALLOW_SYMBOLIC_LINK = 1;

	my $PREFIX = substShellPatterns($options{'prefix'}) || File::Spec->catfile('','usr','local');
	my $end = File::Spec->catfile('usr','local');
	if ($PREFIX =~ /\Q$end\E$/) {
		$end = File::Spec->catfile("$PREFIX",'..','..','etc');
	}
	else {
		$end = File::Spec->catfile("$PREFIX",'..','etc');
	}
	my $ETCPREFIX = substShellPatterns($options{'etc-prefix'}) || $end;
	my $MANPREFIX = substShellPatterns($options{'man-prefix'}) || File::Spec->catfile($PREFIX,'man');
	my $TEXPREFIX = substShellPatterns($options{'tex-prefix'}) || File::Spec->catfile($PREFIX,'share','texmf');

	$INSTALLDIRECTORY = File::Spec->catfile("$PREFIX",'lib','autolatex');
	$BINDIRECTORY = File::Spec->catfile("$PREFIX",'bin');
	$ETCDIRECTORY = File::Spec->catfile("$ETCPREFIX",'autolatex');
	$MANDIRECTORY = File::Spec->catfile("$MANPREFIX",'man1');
	$LOCALEDIRECTORY = File::Spec->catfile("$PREFIX",'share', 'locale');
	$ICONDIRECTORY = File::Spec->catfile("$PREFIX",'share', 'icons');
	$STYDIRECTORY = File::Spec->catfile("$TEXPREFIX",'tex','latex','autolatex');
	$GEDITPLUGINDIRECTORY = File::Spec->catfile("$PREFIX",'lib','gedit','plugins','autolatex');
	$GSETTINGSSCHEMADIRECTORY = File::Spec->catfile("$PREFIX",'share','glib-2.0','schemas');
}

# Run the action
if ($options{'action'} ne 'unknow') {
	eval("DO_".$options{'action'}.'(%options);');
	die"$@\n" if ($@);
}
else {
	DO_createMakefile(%options);
}

exit(0);

__END__

