@echo off

REM build driver scripts

python driver_packager.py packeger_configs\\deployment_service_driver.ini
python driver_packager.py packeger_configs\\connect_command.ini
python driver_packager.py packeger_configs\\deploy_from_template_command.ini
python driver_packager.py packeger_configs\\destroy_vm_command.ini

copy orchestration_service\driver.py "vCenterShellPackage\\Resource Scripts\\Deploy App.py" /Y
copy vlan_service\vlan_driver.py "vCenterShellPackage\\Resource Scripts\\Connect All.py" /Y


REM build vCenterShell package
python shell_packager.py vCenterShell