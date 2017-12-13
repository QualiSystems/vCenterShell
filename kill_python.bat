@echo off
::taskkill /im python.exe /f
wmic Path win32_process Where "CommandLine Like '%%\\ExecutionServer\\%%python.exe%%'" Call Terminate
wmic Path win32_process Where "CommandLine Like '%%\\ProgramData\\QualiSystems\\%%python.exe%%'" Call Terminate