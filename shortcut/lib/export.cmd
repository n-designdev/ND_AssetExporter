
pushd %~dp0
cd ../pycode

<<<<<<< HEAD:shortcut/lib/export.cmd
set USE_OPENGL_VIEWPORT=1

"Y:\tool\MISC\Python2710_amd64_vs2010\python.exe" main.py ""
=======
"Y:\tool\MISC\Python2710_amd64_vs2010\python.exe" main.py "%1"
>>>>>>> 18a7f875b981ba3d75aff23eadf9a004e0482213:shortcut/export.cmd

popd

pause
