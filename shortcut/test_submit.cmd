
pushd %~dp0
cd ../pycode

"Y:\tool\MISC\Python2710_amd64_vs2010\python.exe" -c "import back_starter; back_starter.test_submit()" "%1"

popd

pause
