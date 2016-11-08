import os
import subprocess
from urllib2 import urlopen
from cloudshell.cp.vcenter.common.utilites.common_utils import fixurl
from cloudshell.cp.vcenter.models.VMwarevCenterResourceModel import VMwarevCenterResourceModel

OVF_DESTENATION_FORMAT = 'vi://{0}:{1}@{2}/{3}/host/{4}{5}'

COMPLETED_SUCCESSFULLY = 'Completed successfully'
NO_SSL_PARAM = '--noSSLVerify'
ACCEPT_ALL_PARAM = '--acceptAllEulas'
POWER_ON_PARAM = '--powerOn'
POWER_OFF_PARAM = '--powerOffTarget'
VM_FOLDER_PARAM = '--vmFolder={0}'
VM_NAME_PARAM = '--name={0}'
DATA_STORE_PARAM = '--datastore={0}'
RESOURCE_POOL_PARAM_TO_URL = '/Resources/{0}'


class OvfImageDeployerService(object):
    def __init__(self, resource_model_parser):
        self.resource_model_parser = resource_model_parser

    def deploy_image(self, vcenter_data_model, image_params, logger):
        """
        Receives ovf image parameters and deploy it on the designated vcenter
        :param VMwarevCenterResourceModel vcenter_data_model:
        :type image_params: vCenterShell.vm.ovf_image_params.OvfImageParams
        :param logger:
        """
        ovf_tool_exe_path = vcenter_data_model.ovf_tool_path

        self._validate_url_exists(ovf_tool_exe_path, 'OVF Tool')

        args = self._get_args(ovf_tool_exe_path, image_params)
        logger.debug('opening ovf tool process with the params: {0}'.format(','.join(args)))
        process = subprocess.Popen(args, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)

        logger.debug('communicating with ovf tool')
        result = process.communicate()
        process.stdin.close()

        if result:
            res = '\n\r'.join(result)
        else:
            if image_params.user_arguments.find('--quiet') == -1:
                raise Exception('no result has return from the ovftool')
            res = COMPLETED_SUCCESSFULLY

        logger.info('communication with ovf tool results: {0}'.format(res))
        if res.find(COMPLETED_SUCCESSFULLY) > -1:
            return True

        image_params.connectivity.password = '******'
        args_for_error = ' '.join(self._get_args(ovf_tool_exe_path, image_params))
        logger.error('error deploying image with the args: {0}, error: {1}'.format(args_for_error, res))
        raise Exception('error deploying image with the args: {0}, error: {1}'.format(args_for_error, res))

    def _get_args(self, ovf_tool_exe_path, image_params):
        """
        :type image_params: vCenterShell.vm.ovf_image_params.OvfImageParams
        """
        # create vm name
        vm_name_param = VM_NAME_PARAM.format(image_params.vm_name)

        # datastore name
        datastore_param = DATA_STORE_PARAM.format(image_params.datastore)

        # power state
        # power_state = POWER_ON_PARAM if image_params.power_on else POWER_OFF_PARAM
        # due to hotfix 1 for release 1.0,
        # after deployment the vm must be powered off and will be powered on if needed by orchestration driver

        power_state = POWER_OFF_PARAM

        # build basic args
        args = [ovf_tool_exe_path,
                NO_SSL_PARAM,
                ACCEPT_ALL_PARAM,
                power_state,
                vm_name_param,
                datastore_param]
        # append user folder
        if hasattr(image_params, 'vm_folder') and image_params.vm_folder:
            vm_folder_str = VM_FOLDER_PARAM.format(image_params.vm_folder)
            args.append(vm_folder_str)

        # append args that are user inputs
        if hasattr(image_params, 'user_arguments') and image_params.user_arguments:
            args += [key.strip()
                     for key in image_params.user_arguments.split(',')]

        # get ovf destination
        ovf_destination = self._get_ovf_destenation(image_params)

        image_url = image_params.image_url
        self._validate_image_exists(image_url)

        # set location and destination
        args += [image_url,
                 ovf_destination]

        return args

    def _get_ovf_destenation(self, image_params):
        resource_pool_str = ''
        if image_params.resource_pool:
            resource_pool_str = RESOURCE_POOL_PARAM_TO_URL.format(image_params.resource_pool)

        # connection to the vcenter and the path of the cluster name of the deployed image
        ovf_destination = OVF_DESTENATION_FORMAT. \
            format(image_params.connectivity.username,
                   image_params.connectivity.password,
                   str(image_params.connectivity.host).encode('ascii'),
                   str(image_params.datacenter).encode('ascii'),
                   str(image_params.cluster).encode('ascii'),
                   str(resource_pool_str).encode('ascii'))
        return fixurl(ovf_destination)

    @staticmethod
    def fix_param(param):
        if str(param).find(' ') > -1:
            return '\"{0}\"'.format(param)
        return param

    def _validate_image_exists(self, image_url):
        self._validate_url_exists(image_url, 'Image')

    @staticmethod
    def _validate_url_exists(image_url, type_name):
        try:
            f = urlopen(image_url)
            if f:
                return True
        except Exception:  # invalid URL
            exists = os.path.exists(image_url) and os.path.isfile(image_url)
            if exists:
                return True

        raise ValueError('{0} cannot be open at: "{1}"'.format(type_name, image_url))
