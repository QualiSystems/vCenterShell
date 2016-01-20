@ECHO OFF
SET /p VERSION=<version.txt
SET PACKAGE_NAME=vCenterShell_%VERSION%.zip
SET ZIP=7z a -bd -r
%ZIP% %PACKAGE_NAME% models 
IF %ERRORLEVEL% NEQ 0 GOTO Error

%ZIP% %PACKAGE_NAME% pycommon 
IF %ERRORLEVEL% NEQ 0 GOTO Error

%ZIP% %PACKAGE_NAME% vCenterShell\commands
IF %ERRORLEVEL% NEQ 0 GOTO Error

%ZIP% %PACKAGE_NAME% vCenterShell\__init__.py
IF %ERRORLEVEL% NEQ 0 GOTO Error

pushd vCenterShell
%ZIP% ..\%PACKAGE_NAME% Bootstrapper.py 
IF %ERRORLEVEL% NEQ 0 GOTO Error

%ZIP% ..\%PACKAGE_NAME% __main__.py 
IF %ERRORLEVEL% NEQ 0 GOTO Error

popd
ECHO.
ECHO Packaging of %PACKAGE_NAME% succeeded
ECHO.

GOTO End

:Error
ECHO Packaging of %PACKAGE_NAME% failed

:End

