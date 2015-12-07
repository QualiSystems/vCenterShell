@ECHO OFF
pushd ..\Packages
%programdata%\Qualisystems\QsPython27\Scripts\pip install -v -r .\requirements.txt
popd