#!/bin/sh

#############################################################
echo "Generating the pot file..."

xgettext -L perl -k_T --from-code=UTF-8 --files-from=po/POTFILES_cli.in -o po/template_cli.pot || exit 1

xgettext -L perl -k_T --from-code=UTF-8 --files-from=po/POTFILES_gtk.in -o po/template_gtk.pot || exit 1

xgettext -L python -k_T --from-code=UTF-8 --files-from=po/POTFILES_gedit.in -o po/template_gedit.pot || exit 1

#############################################################
echo "Updating the existing translations..."

for PO_FILE in po/*/LC_MESSAGES/autolatex.po
do
	msgmerge --backup=none -U "$PO_FILE" "po/template_cli.pot" || exit 1
done

for PO_FILE in po/*/LC_MESSAGES/autolatexgtk.po
do
	msgmerge --backup=none -U "$PO_FILE" "po/template_gtk.pot" || exit 1
done

for PO_FILE in po/*/LC_MESSAGES/geditautolatex.po
do
	msgmerge --backup=none -U "$PO_FILE" "po/template_gedit.pot" || exit 1
done
