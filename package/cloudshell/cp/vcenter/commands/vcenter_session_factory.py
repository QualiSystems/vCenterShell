from pyVim.connect import SmartConnect, Disconnect
from cloudshell.cp.vcenter.common.vcenter.vmomi_service import pyVmomiService


class VCenterSession(object):
    def __init__(self, session, vcenter_resource_model, resource_context):
        self.session = session
        self.vcenter_resource_model = vcenter_resource_model
        self.resource_context = resource_context
        self.pv_service = pyVmomiService(SmartConnect, Disconnect)

    def __enter__(self):
        user = self.vcenter_resource_model.user
        encrypted_pass = self.vcenter_resource_model.password
        vcenter_url = self.resource_context.address
        password = self.session.DecryptPassword(encrypted_pass).Value

        self.si = self.pv_service.connect(vcenter_url, user, password, 443)
        return self.si

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.pv_service.disconnect(self.si)


class VCenterSessionFactory(object):
    @staticmethod
    def create_vcenter_session(session, vcenter_resource_model, resource_context):
        return VCenterSession(session, vcenter_resource_model, resource_context)
