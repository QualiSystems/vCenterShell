
def get_vm_custom_param(vm_custom_params, param_name):
    """
    :param list[VmCustomParam] vm_custom_params:
    :param param_name:
    :return:
    """
    for param in vm_custom_params:
        if param.Name == param_name:
            return param
    return None