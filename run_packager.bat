@echo off

REM build driver scripts

python driver_packager.py packeger_configs\\packager_config_deployment_service_driver.txt deployment_service Deploy
python driver_packager.py packeger_configs\\packager_config_vCenterShell.txt vCenterShell "Deploy From Template"
python driver_packager.py packeger_configs\\packager_config_vCenterShell.txt vCenterShell "Destroy VM"
python driver_packager.py packeger_configs\\packager_config_vCenterShell.txt vCenterShell Connect
copy orchestration_service\driver.py "vCenterShellPackage\\Resource Scripts\\Deploy App.py" /Y
copy vlan_service\vlan_driver.py "vCenterShellPackage\\Resource Scripts\\Connect All.py" /Y


REM build vCenterShell package
python shell_packager.py vCenterShell