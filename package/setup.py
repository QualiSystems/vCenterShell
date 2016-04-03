from setuptools import setup, find_packages
import os

with open(os.path.join('version.txt')) as version_file:
    version_from_file = version_file.read().strip()

with open('requirements.txt') as f_required:
    required = f_required.read().splitlines()

with open('test_requirements.txt') as f_tests:
    required_for_tests = f_tests.read().splitlines()

setup(
        name="cloudshell-cp-vcenter",
        url='https://github.com/QualiSystems/vCenterShell',
        author="Quali",
        author_email="support@quali.com",
        description=("This Shell enables setting up vCenter as a cloud provider in CloudShell. "
                     "It supports connectivity, and adds new deployment types for apps which can be used in "
                     "CloudShell sandboxes."),
        packages=find_packages(),
        test_suite='nose.collector',
        test_requires=required_for_tests,
        package_data={'': ['*.txt']},
        install_requires=required,
        version=version_from_file,
        include_package_data=True,
        keywords="sandbox cloud virtualization vcenter cmp cloudshell",
        classifiers=[
            "Development Status :: 5 - Production/Stable",
            "Programming Language :: Python :: 2.7",
            "Topic :: Software Development :: Libraries",
            "License :: OSI Approved :: Apache Software License",
        ]

)
