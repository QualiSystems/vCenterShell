@echo off
python -m pip install qpm --no-cache-dir --upgrade
python -m qpm pack --package_name vCenterShell
copy version.txt package/version.txt /Y
