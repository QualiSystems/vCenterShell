@echo off

REM build driver scripts

python driver_packager.py packeger_configs\\deployment_service_driver.ini
python driver_packager.py packeger_configs\\deploy_from_template_command.ini
python driver_packager.py packeger_configs\\destroy_vm_command.ini
python driver_packager.py packeger_configs\\power_on_command.ini
python driver_packager.py packeger_configs\\power_off_command.ini
python driver_packager.py packeger_configs\\refresh_ip_command.ini
python driver_packager.py packeger_configs\\connect_command.ini
python driver_packager.py packeger_configs\\vlan_auto_service.ini
python driver_packager.py packeger_configs\\orchestration_service.ini

python driver_packager.py packeger_configs\\deployed_app_proxy_connect.ini
python driver_packager.py packeger_configs\\deployed_app_proxy_power_on.ini
python driver_packager.py packeger_configs\\deployed_app_proxy_power_off.ini
python driver_packager.py packeger_configs\\deployed_app_proxy_destroy_vm.ini
python driver_packager.py packeger_configs\\deployed_app_proxy_refresh_ip.ini

python driver_packager.py packeger_configs\\environment_scripts.ini

REM build vCenterShell package
python shell_packager.py vCenterShell