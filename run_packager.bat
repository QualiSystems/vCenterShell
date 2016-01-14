@echo off

REM build driver scripts

python driver_packager.py packeger_configs\\deployment_service_driver.ini
python driver_packager.py packeger_configs\\deploy_from_template_command.ini
python driver_packager.py packeger_configs\\destroy_vm_command.ini
python driver_packager.py packeger_configs\\power_on_command.ini
python driver_packager.py packeger_configs\\power_off_command.ini
python driver_packager.py packeger_configs\\connect_command.ini
python driver_packager.py packeger_configs\\vlan_auto_service.ini
python driver_packager.py packeger_configs\\orchestration_service.ini

copy environment_scripts\connect_all.py "vCenterShellPackage\\Resource Scripts\\Connect All.py" /Y


REM build vCenterShell package
python shell_packager.py vCenterShell