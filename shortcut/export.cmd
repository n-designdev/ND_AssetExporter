
pushd %~dp0
cd ../pycode

set USE_OPENGL_VIEWPORT=1
call X:\MSTB4\Data\90_TOOLS\dpx_env\maya\__env__.bat

"Y:\tool\MISC\Python2710_amd64_vs2010\python.exe" main.py ""

popd

pause
