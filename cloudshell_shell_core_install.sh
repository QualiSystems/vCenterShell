#!/bin/bash
if [ "${CLOUD_SHELL_SHELL_CORE}" -eq 1 ]
then
    pip install "cloudshell-shell-core>=2.0.0,<2.1.0" --extra-index-url https://testpypi.python.org/simple
else
    pip install "cloudshell-shell-core>=2.3.0,<2.4.0" --extra-index-url https://testpypi.python.org/simple
fi