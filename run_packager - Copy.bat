@echo off

REM build driver scripts
del /F /Q "vCenterShellPackage\Resource Scripts\."
del /F /Q "vCenterShellPackage\Topology Scripts\."

REM vCenter Driver package
python driver_packager.py package_specs\\vcentershell_driver.ini

REM build vCenterShell package
python shell_packager.py vCenterShell