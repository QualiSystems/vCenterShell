#!/bin/bash
if [ "${CLOUD_SHELL_SHELL_CORE}" -eq 1 ]
then
	echo "Running vCenter Tests"
    python runtests.py --with-coverage  --cover-package=package --exclude-dir=integration
else
	echo "Running static VM Tests"
    python runtestsStaticVM.py --with-coverage  --cover-package=package --exclude-dir=integration
fi 