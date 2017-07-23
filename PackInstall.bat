@echo off
call run_packager.bat
python -m qpm install --package_name vCenterShell
