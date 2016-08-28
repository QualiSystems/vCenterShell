#!/bin/bash
if [ "${CLOUD_SHELL_SHELL_CORE}" -eq 1 ]
then
    python runtests.py --with-coverage  --cover-package=package --exclude-dir=integration
else
    python runtestsStaticVM.py --with-coverage  --cover-package=package --exclude-dir=integration
fi 