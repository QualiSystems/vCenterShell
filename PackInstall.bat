@echo off
python -m pip install qpm --no-cache-dir --upgrade
python -m qpm pack --package_name vCenterShell
python -m qpm install --package_name vCenterShell
