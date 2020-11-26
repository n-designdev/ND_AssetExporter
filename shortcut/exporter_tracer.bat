@echo off
pushd %~dp0
cd ../pycode
set USE_OPENGL_VIEWPORT=1set time2=%time: =0%
set mm=%date:~0,4%
set dd=%date:~0,4%
set time2=%time: =0%
set hh=%time2:~0,2%
set mn=%time2:~3,2%
set ss=%time2:~6,2%
"Y:\tool\MISC\Python2710_amd64_vs2010\python.exe" main.py "" > ..\\log\\%mm%%dd%%hh%%mn%%ss%_%USERNAME%.txt 2>&1

popd

pause
