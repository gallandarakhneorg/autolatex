#/bin/sh

#############################################################
echo "Generating the pot file..."

xgettext -L perl -k_T --from-code=UTF-8 --files-from=po/POTFILES_cli.in -o po/template_cli.pot || exit 1

xgettext -L perl -k_T --from-code=UTF-8 --files-from=po/POTFILES_ui.in -o po/template_ui.pot || exit 1

xgettext -L perl -k_T --from-code=UTF-8 --files-from=po/POTFILES_gtk.in -o po/template_gtk.pot || exit 1

#############################################################
echo "Updating the existing translations..."

for PO_FILE in po/*/LC_MESSAGES/autolatex.po
do
	msgmerge -U "$PO_FILE" "po/template_cli.pot" || exit 1
done

for PO_FILE in po/*/LC_MESSAGES/autolatexgui.po
do
	msgmerge -U "$PO_FILE" "po/template_ui.pot" || exit 1
done

for PO_FILE in po/*/LC_MESSAGES/autolatexgtk.po
do
	msgmerge -U "$PO_FILE" "po/template_gtk.pot" || exit 1
done
