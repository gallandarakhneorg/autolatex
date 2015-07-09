@ECHO OFF
WHERE python3
IF %ERRORLEVEL% NEQ 0 perl %~dp0\autolatex-gtk.pl %*
ELSE python3 %~dp0\autolatex-config.py %*
