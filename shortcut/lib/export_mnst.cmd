
pushd %~dp0
cd ../pycode

set USE_OPENGL_VIEWPORT=1

"C:\Program Files\Shotgun\Python\python.exe" main.py "%1"

popd

pause
