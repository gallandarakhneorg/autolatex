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

AutoLaTeX::GUI::Gtk::TranslatorPanel - A GTK panel for translator management

=head1 DESCRIPTION

AutoLaTeX::GUI::Gtk::TranslatorPanel is a Perl module, which permits to
display a Gtk panel that manages AutoLaTeX translators.

=head1 METHOD DESCRIPTIONS

This section contains only the methods in GtkTranslatorPanel.pm itself.

=over

=cut

package AutoLaTeX::GUI::Gtk::TranslatorPanel;

@ISA = qw( Gtk2::Table AutoLaTeX::GUI::Gtk::WidgetUtil AutoLaTeX::GUI::AbstractTranslatorPanel );
@EXPORT = qw();
@EXPORT_OK = qw();

use strict;
use vars qw(@ISA @EXPORT @EXPORT_OK $VERSION);
use Exporter;

use Glib qw(TRUE FALSE);
use Gtk2;
use Gtk2::SimpleList;

use AutoLaTeX::Core::Util;
use AutoLaTeX::Core::Locale;
use AutoLaTeX::Core::Config;
use AutoLaTeX::Core::Translator;
use AutoLaTeX::GUI::AbstractTranslatorPanel;
use AutoLaTeX::GUI::Gtk::WidgetUtil;

#------------------------------------------------------
#
# Global vars
#
#------------------------------------------------------

# Version number
my $VERSION = "6.0" ;

#------------------------------------------------------
#
# Functions
#
#------------------------------------------------------

=pod

=item * new(\%\%\%\%;$)

Contructor.

Parameters are:

=over 4

=item the current configuration extracted from the configuration files.

=item the system configuration extracted from the configuration file.

=item the user configuration extracted from the configuration file.

=item the project configuration extracted from the configuration file.

=item an object on which the subroutine C<onTranslatorPanelStateChanged()> is available.

=back

=cut
sub new(\%\%\%\%;$) : method {
	my $proto = shift;
	my $class = ref($proto) || $proto;

	my $self = bless( $class->SUPER::new(
						2, #rows
						2, #columns
						FALSE), #non uniform
			$class ) ;

	die("The first parameter of AutoLaTeX::GUI::Gtk::TranslatorPanel::new() should be a hastable\nIf you pass a %v variable, please use the \%v syntax instead.\n")
		unless ((!defined($_[0]))||(isHash($_[0])));
	$self->attr('CONFIGURATIONS','FULL') = $_[0];

	die("The second parameter of AutoLaTeX::GUI::Gtk::TranslatorPanel::new() should be a hastable\nIf you pass a %v variable, please use the \%v syntax instead.\n")
		unless ((!defined($_[1]))||(isHash($_[1])));
	$self->attr('CONFIGURATIONS','SYSTEM') = $_[1];

	die("The third parameter of AutoLaTeX::GUI::Gtk::TranslatorPanel::new() should be a hastable\nIf you pass a %v variable, please use the \%v syntax instead.\n")
		unless ((!defined($_[2]))||(isHash($_[2])));
	$self->attr('CONFIGURATIONS','USER') = $_[2];

	die("The forth parameter of AutoLaTeX::GUI::Gtk::TranslatorPanel::new() should be a hastable\nIf you pass a %v variable, please use the \%v syntax instead.\n")
		unless ((!defined($_[3]))||(isHash($_[3])));
	$self->attr('CONFIGURATIONS','PROJECT') = $_[3];

	$self->attr('PANEL_LISTENERS') = [ $_[4] ] if ($_[4]);


	# Initialization
	$self->initializeTranslatorPanel();

	return $self;
}

=pod

=item * initControls()

Initializing the controls.

=cut
sub initControls() : method {
	my $self = shift;

	# Label
	my $label = Gtk2::Label->new($self->localeGet(_T("List of available translators:\n(click on the three left columns to change the loading state of the translators)")));
	$self->attach ($label, 
				0,1,0,1, # left, right, top and bottom columns
				'expand','shrink', # x and y options
				0,0); # horizontal and vertical paddings

	# Translator list and associated text
	my $translatorList = Gtk2::SimpleList->new (
					'system', 'pixbuf', 
					'user', 'pixbuf', 
					'project', 'pixbuf',
					'name', 'text',
					'description', 'text');
	$translatorList->set_headers_clickable (FALSE);
	$translatorList->set_headers_visible (FALSE);
	$self->attr('TRANSLATOR_LIST') = $translatorList;

	my $translatorListScroll = Gtk2::ScrolledWindow-> new();
	$translatorListScroll->add ($translatorList);
	$translatorListScroll->set_size_request (500,400);
	$translatorListScroll->set_policy ('automatic','automatic');
	$translatorListScroll->set_shadow_type ('in');

	$self->attach ($translatorListScroll, 
				0,1,1,2, # left, right, top and bottom columns
				['fill','expand'],['fill','expand'], # x and y options
				5,5); # horizontal and vertical paddings

	# Management buttons
	my $buttonAlignment = Gtk2::VButtonBox->new ();
	$buttonAlignment->set_layout_default('start');
	$self->attach ($buttonAlignment, 
				1,2,0,2, # left, right, top and bottom columns
				'shrink',['fill','expand'], # x and y options
				5,5); # horizontal and vertical paddings

	my $addButton = Gtk2::Button->new_from_stock ('gtk-add');
	$self->connectSignal($addButton,'clicked','onTranslatorAdded');
	$addButton->set_sensitive( FALSE ) ;
	$self->attr('BUTTONS','addTranslator') = $addButton;
	$buttonAlignment->add ($addButton);

	my $editButton = Gtk2::Button->new_from_stock ('gtk-edit');
	$self->connectSignal($editButton,'clicked','onTranslatorEdited');
	$editButton->set_sensitive( FALSE ) ;
	$self->attr('BUTTONS','editTranslator') = $editButton;
	$buttonAlignment->add ($editButton);

	my $deleteButton = Gtk2::Button->new_from_stock ('gtk-delete');
	$self->connectSignal($deleteButton,'clicked','onTranslatorDeleted');
	$deleteButton->set_sensitive( FALSE ) ;
	$self->attr('BUTTONS','deleteTranslator') = $deleteButton;
	$buttonAlignment->add ($deleteButton);

	# Help
	$buttonAlignment->add (Gtk2::HSeparator->new ());
	$buttonAlignment->add ($self->makeLegend($self->getLevelIcon('system'), _T('All users')));
	$buttonAlignment->add ($self->makeLegend($self->getLevelIcon('user'), _T('Current usr')));
	$buttonAlignment->add ($self->makeLegend($self->getLevelIcon('project'), _T('Current project')));
	$buttonAlignment->add (Gtk2::HSeparator->new ());
	$buttonAlignment->add ($self->makeLegend($self->getLevelIcon('system'), _T('Loaded, no conflict')));
	$buttonAlignment->add ($self->makeLegend($self->getConflictLevelIcon('system'), _T('Loaded, conflict')));
	$buttonAlignment->add ($self->makeLegend($self->getRedLevelIcon('system'), _T('Not loaded')));
	$buttonAlignment->add ($self->makeLegend($self->getGrayedLevelIcon('system'), _T('Unspecified, no conflict')));
	$buttonAlignment->add ($self->makeLegend($self->getGrayedConflictLevelIcon('system'), _T('Unspecified, conflict')));
}

sub makeLegend($$;$) {
	my $self = shift;
	my $icon = shift;
	my $textlabel = shift;
	my $topPadding = shift || 0;

	my $legendAlignment = Gtk2::Table->new (5,2);

	my $iconLabel = Gtk2::Image->new_from_pixbuf($icon);
	$legendAlignment->attach ($iconLabel, 0, 1, 0, 1, 'fill', 'fill', 0, $topPadding);

	my $text = Gtk2::Label->new ($self->localeGet($textlabel));
	$legendAlignment->attach ($text, 1, 2, 0, 1, 'fill', 'fill', 5, $topPadding);

	return $legendAlignment;
}

=pod

=item * initializeTranslatorPanel()

Initializing the panel content before displaying.

This method read the list of the translators and
fill the attribute C<{'DATA'}{'translators'}>.

=cut
sub initializeTranslatorPanel() : method {
	my $self = shift;
	$self->SUPER::initializeTranslatorPanel();
	$self->initLocale('autolatexgtk');
	$self->initControls();
	$self->detectTranslatorConflicts();
	$self->fillTranslatorList();
	$self->notifyListeners();
	$self->connectGtkSignals();
}

=pod

=item * getInclusionStateIcon($$)

Replies the icon that corresponds to the inclusion state of a translator at the specified level.

=over 4

=item level

=item translator name

=cut
sub getInclusionStateIcon($$) : method {
	my $self = shift;
	my $level = shift;
	my $name = shift;

	# Does the translator has a conflict?
	my $conflict = $self->hasTranslatorConflict($level,$name);

	if ($self->hasattr('TRANSLATORS',"$name",'included',"$level")) {
		my $val = $self->attr('TRANSLATORS',"$name",'included',"$level");
		if (defined($val)) {
			if ($val) {
				return $self->getConflictLevelIcon($level) if ($conflict);
				return $self->getLevelIcon($level);
			}
			else {
				return $self->getIcon("warning.png") if ($conflict);
				return $self->getRedLevelIcon($level);
			}
		}
	}
	return $self->getGrayedConflictLevelIcon($level) if ($conflict);
	return $self->getGrayedLevelIcon($level);
}

=pod

=item * detectTranslatorConflicts()

Detect translator conflicts.

=cut
sub detectTranslatorConflicts() : method {
	my $self = shift;
	my %conflicts = detectConflicts(%{$self->attr('TRANSLATORS')});
	# Parse conflict data structure to extract the names of the
	# translators under conflict
	foreach my $k (keys %conflicts) {
		my %trs = ();
		foreach my $source (keys %{$conflicts{$k}}) {
			foreach my $t (keys %{$conflicts{$k}{$source}}) {
				$trs{$t} = 1;
			}
		}
		my @trs = keys %trs;
		$conflicts{$k} = \@trs;
	}
	if (!$self->hasProject()) {
		delete $conflicts{'project'};
	}
	$self->attr('TRANSLATOR_CONFLICTS') = \%conflicts;
}

=pod

=item * hasTranslatorConflict()

Replies if a conflict exists for the specified translator and level.

=over 4

=item level

=item translator name

=back

=cut
sub hasTranslatorConflict($$) : method {
	my $self = shift;
	my $level = shift;
	my $name = shift;
	if (($self->hasattr('TRANSLATOR_CONFLICTS',"$level"))&&
	    (isArray($self->attr('TRANSLATOR_CONFLICTS',"$level")))) {
		return arrayContains(@{$self->attr('TRANSLATOR_CONFLICTS',"$level")},$name);
	}
	return 0;
}

=pod

=item * isUnderConflict()

Replies if a conflict exists.

=cut
sub isUnderConflict() : method {
	my $self = shift;
	if ($self->hasattr('TRANSLATOR_CONFLICTS')) {
		my $conflicts = $self->attr('TRANSLATOR_CONFLICTS');
		my $lastlevel = $self->hasProject() ? $ALL_LEVELS[$#ALL_LEVELS] : $ALL_LEVELS[$#ALL_LEVELS-1];
		return 1 if ((isArray($conflicts->{"$lastlevel"}))&&
			     (@{$conflicts->{"$lastlevel"}}));
		
	}
	return 0;
}

=pod

=item * fillTranslatorList()

Fill the list of translators.

=cut
sub fillTranslatorList() : method {
	my $self = shift;

	my @keys = sort keys %{$self->attr('TRANSLATORS')};

	@{$self->attr('TRANSLATOR_LIST')->{'data'}} = ();

	my ($systemIcon, $userIcon, $projectIcon);

	foreach my $trans (@keys) {
		$systemIcon = $self->getInclusionStateIcon('system',$trans);
		$userIcon = $self->getInclusionStateIcon('user',$trans);
		$projectIcon = $self->hasProject() ? $self->getInclusionStateIcon('project',$trans) : undef;

		push @{$self->attr('TRANSLATOR_LIST')->{'data'}}, 
			[ 
				$systemIcon,
				$userIcon,
				$projectIcon,
				$trans,
				$self->attr('TRANSLATORS',"$trans",'human-readable'),
			];
	}
}

=pod

=item * connectGtkSignals()

Differed connection of GTK signals to widgets.

=cut
sub connectGtkSignals() : method {
	my $self = shift;
	$self->connectSignal($self->attr('TRANSLATOR_LIST'),'row-activated','onTranslatorEdit');
	$self->connectSignal($self->attr('TRANSLATOR_LIST'),'button-press-event','onTranslatorClick');
	$self->connectSignal($self->attr('TRANSLATOR_LIST'),'cursor-changed','onTranslatorSelected');
}

=pod

=item * getTranslatorDataAt($)

Replies the data associated to the translator at the specified index

=cut
sub getTranslatorDataAt($) : method {
	my $self = shift;
	my $row = $self->attr('TRANSLATOR_LIST')->{'data'}[$_[0]];
	$self->attr('TRANSLATORS',$row->[3]);
}

=pod

=item * updateIcons($$)

Update the icons for the translator that support the given source
extension from the specified level.

=over 4

=item the level for which the update must be done.

=item the source extension that is the source of this update.

=back

=cut
sub updateIcons($$) : method {
	my $self = shift;
	my $level = shift;
	my $source = shift;

	my $levelIndex = arrayIndexOf(@ALL_LEVELS,$level);

	for(my $column=$levelIndex; $column<@ALL_LEVELS; $column++) {
		my $clevel = $ALL_LEVELS[$column];
		if (($clevel ne 'project')||($self->hasProject())) {
			for(my $idxTrans=0; $idxTrans<@{$self->attr('TRANSLATOR_LIST')->{'data'}}; $idxTrans++) {
				my $transData = $self->getTranslatorDataAt($idxTrans);
				if ($source eq $transData->{'full-source'}) {
					my $icon = $self->getInclusionStateIcon($clevel,$transData->{'name'});
					$self->attr('TRANSLATOR_LIST')->{'data'}[$idxTrans][$column] = $icon;
				}
			}
		}
	}
}	

=pod

=item * notifyListeners()

Notify listeners about a change of the stateof this panel.

=cut
sub notifyListeners() : method {
	my $self = shift;
	my $conflict = $self->isUnderConflict();
	if (($self->hasattr('PANEL_LISTENERS'))&&(isArray($self->attr('PANEL_LISTENERS')))) {
		foreach my $listener (@{$self->attr('PANEL_LISTENERS')}) {
			if ($listener->can('onTranslatorPanelStateChanged')) {
				$listener->onTranslatorPanelStateChanged($self,$conflict);
			}
		}
	}
}

#
#------------------------------------- SIGNALS
#

sub onTranslatorSelected(@) : method {
	my $self = shift;
	my $canWrite = 0;
	#my @sel = $self->attr('TRANSLATOR_LIST')->get_selected_indices ();
	#if (@sel) {
	#	my $sel = pop @sel;
	#	if ($sel>=0) {
	#		my $data = $self->getTranslatorDataAt($sel);
	#		if ($data) {
	#			$canWrite = ((($data->{'level'} eq 'system')&&($self->isAdminUser()))||
	#					    ($data->{'level'} eq 'user')||
	#					    (($data->{'level'} eq 'project')&&($self->hasProject())));
	#		}
	#	}
	#}
	$self->attr('BUTTONS','editTranslator')->set_sensitive ($canWrite);
	$self->attr('BUTTONS','deleteTranslator')->set_sensitive ($canWrite);
}

sub onTranslatorClick(@) : method {
	my $self = shift;
	my $event = $_[1]; #Gtk2::Gdk::Event
	my ($x,$y) = $event->get_coords ();
	my ($path,$column,$cell_x,$cell_y) = $_[0]->get_path_at_pos ($x,$y);
	if ($path) {
		my @indices = $path->get_indices ();
		my $title = $column->get_title ();
		if ((($title eq 'system')&&($self->isAdminUser()))||
		    ($title eq 'user')||
		    (($title eq 'project')&&($self->hasProject()))) {
			my $index = pop @indices;
			my $data = $self->getTranslatorDataAt($index);
			if (!defined($data->{'included'}{"$title"})) {
				$data->{'included'}{"$title"} = 1;
			}
			elsif ($data->{'included'}{"$title"}) {
				$data->{'included'}{"$title"} = 0;
			}
			else {
				$data->{'included'}{"$title"} = undef;
			}

			$self->detectTranslatorConflicts();

			# Update the icons
			$self->updateIcons($title,$data->{'full-source'});

			# Notify listeners
			$self->notifyListeners();
		}
	}
}

sub onTranslatorAdded(@) : method {
	my $self = shift;
}

sub onTranslatorDeleted(@) : method {
	my $self = shift;
	#
	#my @sel = $self->attr('TRANSLATOR_LIST')->get_selected_indices ();
	#if (@sel) {
	#	foreach my $sel (@sel) {
	#		my $data = $self->getTranslatorDataAt($sel);
	#		if ($data) {
	#			my $canWrite = ((($data->{'level'} eq 'system')&&($self->isAdminUser()))||
	#					    ($data->{'level'} eq 'user')||
	#					    (($data->{'level'} eq 'project')&&($self->hasProject())));
	#		}
	#	}
	#}
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
