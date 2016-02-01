@echo off

REM build driver scripts
del /F /Q "vCenterShellPackage\Resource Scripts\."
del /F /Q "vCenterShellPackage\Topology Scripts\."

python driver_packager.py package_specs\\deployment_service_driver.ini
python driver_packager.py package_specs\\deploy_from_template_command.ini
python driver_packager.py package_specs\\destroy_vm_command.ini
python driver_packager.py package_specs\\power_on_command.ini
python driver_packager.py package_specs\\power_off_command.ini
python driver_packager.py package_specs\\refresh_ip_command.ini
python driver_packager.py package_specs\\connect_command.ini
python driver_packager.py package_specs\\connect_bulk_command.ini
python driver_packager.py package_specs\\vlan_auto_service.ini
python driver_packager.py package_specs\\orchestration_service.ini

python driver_packager.py package_specs\\deployed_app_proxy_connect.ini
python driver_packager.py package_specs\\deployed_app_proxy_power_on.ini
python driver_packager.py package_specs\\deployed_app_proxy_power_off.ini
python driver_packager.py package_specs\\deployed_app_proxy_destroy_vm.ini
python driver_packager.py package_specs\\deployed_app_proxy_refresh_ip.ini

python driver_packager.py package_specs\\environment_connect_all.ini

REM vCenter Driver package
python driver_packager.py package_specs\\vcentershell_driver.ini

REM build vCenterShell package
python shell_packager.py vCenterShell