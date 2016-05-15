from abc import abstractmethod
from cloudshell.api.cloudshell_api import CloudShellAPISession
from cloudshell.cp.vcenter.commands.vcenter_session_factory import VCenterOperationContext
from cloudshell.cp.vcenter.common.model_factory import ResourceModelParser
from cloudshell.cp.vcenter.models.VMwarevCenterResourceModel import VMwarevCenterResourceModel


class ContextBasedService(object):
    @abstractmethod
    def get_objects(self):
        pass

    @abstractmethod
    def context_started(self):
        pass

    @abstractmethod
    def context_ended(self, exc_type, exc_val, exc_tb):
        pass

    def __enter__(self):
        self.context_started()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.context_ended(exc_type, exc_val, exc_tb)


class CloudShellSessionContext(ContextBasedService):
    def __init__(self, context):
        self.context = context

    def get_objects(self):
        return self.context_object

    @staticmethod
    def _get_domain(context):
        # noinspection PyBroadException
        try:
            return context.remote_reservation.domain
        except:
            return context.reservation.domain

    def context_started(self):
        self.context_object = CloudShellAPISession(host=self.context.connectivity.server_address,
                                                   token_id=self.context.connectivity.admin_auth_token,
                                                   username=None,
                                                   password=None,
                                                   domain=CloudShellSessionContext._get_domain(self.context))

        return self.context_object

    def context_ended(self, exc_type, exc_val, exc_tb):
        pass


class CloudShellContextFactory(object):
    def create(self, context):
        return CloudShellSessionContext(context)


class VCenterShellContextFactory(object):
    def __init__(self, resource_model_parser):
        """
        :type resource_model_parser cloudshell.cp.vcenter.common.model_factory.ResourceModelParser
        :param resource_model_parser:
        :return:
        """
        self.resource_model_parser = resource_model_parser

    def create_context(self, session, context):
        vcenter_model = self.resource_model_parser.convert_to_resource_model(context, VMwarevCenterResourceModel)
        return VCenterOperationContext(session, vcenter_model, context)
