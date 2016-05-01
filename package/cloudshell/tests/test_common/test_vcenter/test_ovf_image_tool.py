import unittest
import urllib

from mock import Mock, patch
from cloudshell.cp.vcenter.models.VCenterConnectionDetails import VCenterConnectionDetails

from cloudshell.cp.vcenter.common.vcenter.ovf_service import OvfImageDeployerService

PROCESS = Mock()


class ProccesMock:
    @staticmethod
    def Popen(*args, **kwargs):
        PROCESS.args = args[0]

        return PROCESS


class TestOvfImageService(unittest.TestCase):
    @patch('subprocess.Popen', ProccesMock.Popen)
    def test_deploy_image_success(self):
        PROCESS.communicate = Mock(return_value=['Completed successfully'])
        expected_args = \
            ['dummypath/ovftool.exe',
             '--noSSLVerify',
             '--acceptAllEulas',
             '--powerOffTarget',
             '--name=raz_deploy_image_integration_test',
             '--datastore=aa',
             '--vmFolder=Raz',
             '--vlan="anetwork"',
             'http://192.168.65.88/ovf/Debian 64 - Yoav.ovf',
             'vi://vcenter%20user:password%20to%20vcenter@venter.host.com/QualiSB/host/QualiSB%20Cluster/Resources/LiverPool']
        ovf = OvfImageDeployerService('dummypath/ovftool.exe')
        image_params = Mock()
        image_params.connectivity = VCenterConnectionDetails('venter.host.com', 'vcenter user', 'password to vcenter')

        image_params.datacenter = 'QualiSB'
        image_params.cluster = 'QualiSB Cluster'
        image_params.resource_pool = 'LiverPool'
        image_params.vm_name = 'raz_deploy_image_integration_test'
        image_params.datastore = 'aa'
        image_params.power_on = 'false'
        image_params.vm_folder = 'Raz'
        # image_params.image_url = "C:\\images\\test\\OVAfile121_QS\\OVAfile121_QS.ovf"
        image_params.image_url = "http://192.168.65.88/ovf/Debian 64 - Yoav.ovf"
        image_params.user_arguments = '--vlan="anetwork"'

        vcenter_data_model = Mock()
        vcenter_data_model.ovf_tool_path = 'dummypath/ovftool.exe'

        ovf._validate_url_exists = Mock(return_value=True)

        res = ovf.deploy_image(vcenter_data_model, image_params, logger=Mock())

        self.assertTrue(res)
        self.assertEqual(PROCESS.args, expected_args)
        self.assertTrue(PROCESS.stdin.close.called)

    @patch('subprocess.Popen', ProccesMock.Popen)
    def test_deploy_image_no_communication(self):

        PROCESS.communicate = Mock(return_value=None)
        ovf = OvfImageDeployerService('dummypath/ovftool.exe')
        image_params = Mock()
        image_params.connectivity = VCenterConnectionDetails('venter.host.com', 'vcenter user', 'password to vcenter')

        image_params.datacenter = 'QualiSB'
        image_params.cluster = 'QualiSB Cluster'
        image_params.vm_name = 'raz_deploy_image_integration_test'
        image_params.resource_pool = 'LiverPool'
        image_params.datastore = 'aa'
        # image_params.image_url = "C:\\images\\test\\OVAfile121_QS\\OVAfile121_QS.ovf"
        image_params.image_url = "http://192.168.65.88/ovf/Debian 64 - Yoav.ovf"
        image_params.user_arguments = '--vlan="anetwork"'

        vcenter_data_model = Mock()
        vcenter_data_model.ovf_tool_path = 'dummypath/ovftool.exe'
        ovf._validate_url_exists = Mock(return_value=True)

        self.assertRaises(Exception, ovf.deploy_image, vcenter_data_model, image_params)
        self.assertTrue(PROCESS.stdin.close.called)

    @patch('subprocess.Popen', ProccesMock.Popen)
    def test_deploy_image_error(self):

        PROCESS.communicate = Mock(return_value=['error'])
        ovf = OvfImageDeployerService('dummypath/ovftool.exe')
        image_params = Mock()
        image_params.connectivity = VCenterConnectionDetails('venter.host.com', 'vcenter user', 'password to vcenter')
        image_params.datacenter = 'QualiSB'
        image_params.cluster = 'QualiSB Cluster'
        image_params.resource_pool = 'LiverPool'
        image_params.vm_name = 'raz_deploy_image_integration_test'
        image_params.datastore = 'aa'
        # image_params.image_url = "C:\\images\\test\\OVAfile121_QS\\OVAfile121_QS.ovf"
        image_params.image_url = "http://192.168.65.88/ovf/Debian 64 - Yoav.ovf"

        image_params.user_arguments = '--vlan="anetwork"'

        ovf._validate_url_exists = Mock(return_value=True)

        vcenter_data_model = Mock()
        vcenter_data_model.ovf_tool_path = 'dummypath/ovftool.exe'

        try:
            ovf.deploy_image(vcenter_data_model, image_params, logger=Mock())
            # should not reach here
            self.assertTrue(False)
        except Exception as inst:
            self.assertTrue(inst.message.find('password to vcenter') == -1)
            self.assertTrue(inst.message.find(urllib.quote_plus('******')) > -1)
            self.assertTrue(PROCESS.stdin.close.called)
