from unittest import TestCase
from mock import Mock
from cloudshell.cp.vcenter.common.cloud_shell.conn_details_retriever import ResourceConnectionDetailsRetriever
from  cloudshell.cp.vcenter.models.VMwarevCenterResourceModel import VMwarevCenterResourceModel

class TestConnectionDetailRetriever(TestCase):
    def test_connection_detail_retriever(self):
        session = Mock()
        decrypted_password = Mock()
        decrypted_password.Value = 'decrypted password'
        session.DecryptPassword = Mock(return_value=decrypted_password)
        resource_context = Mock()
        resource_context.address = '192.168.1.1'

        vcenter_data_model = VMwarevCenterResourceModel()
        vcenter_data_model.user = 'uzer'
        vcenter_data_model.password = 'password'

        connection_details = ResourceConnectionDetailsRetriever.get_connection_details(session=session,
                                                                                       vcenter_resource_model=vcenter_data_model,
                                                                                       resource_context=resource_context)


        self.assertEqual(connection_details.host, '192.168.1.1')
        self.assertEqual(connection_details.username, 'uzer')
        self.assertEqual(connection_details.password, 'decrypted password')
