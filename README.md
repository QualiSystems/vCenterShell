[![Build Status](https://travis-ci.org/QualiSystems/vCenterShell.svg?branch=master)](https://travis-ci.org/QualiSystems/vCenterShell) [![Coverage Status](https://coveralls.io/repos/QualiSystems/vCenterShell/badge.svg?branch=develop&service=github)](https://coveralls.io/github/QualiSystems/vCenterShell?branch=develop) [![Code Climate](https://codeclimate.com/github/QualiSystems/vCenterShell/badges/gpa.svg)](https://codeclimate.com/github/QualiSystems/vCenterShell) [ ![Foo](https://qualisystems.getbadges.io/shield/company/qualisystems) ](https://getbadges.io) [![Stories in Ready](https://badge.waffle.io/QualiSystems/vCenterShell.svg?label=ready&title=Ready)](http://waffle.io/QualiSystems/vCenterShell) [![Join the chat at https://gitter.im/QualiSystems/vCenterShell](https://badges.gitter.im/QualiSystems/vCenterShell.svg)](https://gitter.im/QualiSystems/vCenterShell?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge) [![Analytics](https://ga-beacon.appspot.com/UA-72194260-1/QualiSystems/vCenterShell)](https://github.com/QualiSystems/vCenterShell/)


A repository for projects providing out of the box capabilities within CloudShell to define VMWare vCenter instances in CloudShell and leverage vCenter's capabilities to deploy and connect apps in CloudShell sandboxes.

## Projects
* **Deployment Drivers**

    These projects extend CloudShell apps with new deployment types
    * **deploy_from_image**
    App deployment type driver for deploying from vCenter OVF images
    * **deploy_from_template**
    App deployment type driver for cloning from vCenter templates


* **package**

    The vCenter Python package hosted in [PyPi](https://pypi.python.org/). The package contains most of the logic relate
    to working with the vCenter API.

* **vcentershell_driver**

    The CloudShell driver for controlling vCenter via CloudShell.

## Installation
* [QualiSystems CloudShell 7.0](http://www.qualisystems.com/products/cloudshell/cloudshell-overview/)
* [pyvmomi 6.0](https://github.com/vmware/pyvmomi)
* [jsonpickle latest](https://jsonpickle.github.io/)


## Getting Started

1. Download vCenterShell.zip from Releases page
2. Drag it into your CloudShell Portal
3. Set vCenter connection details on the vCenter resource according to your enviorment.
4. Update VM Deployment App to set correct "vCenter Template" attribute according to your enviorment.
4. Reserve Virtualisation Starter environment
5. Add VM Deployment from App/Services for each required virtual application
6. Add VLAN Auto from App/Services for each required virtual network
7. Connect them as needed
8. Run Deploy command on each VM Deployment
9. Run Connect All command

## Links
[VmWare vCenter] (https://github.com/vmware/pyvmomi/tree/master/docs)

## License
[Apache License 2.0](https://github.com/QualiSystems/vCenterShell/blob/master/LICENSE)
