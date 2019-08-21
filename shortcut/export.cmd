
pushd %~dp0
cd ../pycode

set USE_OPENGL_VIEWPORT=1
call X:\MSTB4\Data\90_TOOLS\dpx_env\maya\__env__.bat

"C:\Program Files\Shotgun\Python\python.exe" main.py "%1"

popd

pause
