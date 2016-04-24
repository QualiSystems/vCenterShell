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
    def context_ended(self):
        pass

    def __enter__(self):
        self.context_started()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.context_ended()


class CloudShellSessionContext(ContextBasedService):
    def __init__(self, context):
        self.context = context

    def create_session(self, context):
        """
        Creates session with interaction with CloudShell
        :return:
        :param context: instance of ResourceCommandContext or AutoLoadCommandContext
        :type context: cloudshell.shell.core.context.ResourceCommandContext
        """
        # noinspection PyTypeChecker
        session = CloudShellAPISession(host=context.connectivity.server_address,
                                       token_id=context.connectivity.admin_auth_token,
                                       username=None,
                                       password=None,
                                       domain=CloudShellSessionContext._get_domain(context))
        return session

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
        self.context_object = self.create_session(context=self.context)
        return self.context_object

    def context_ended(self):
        pass


class CompositeContext(ContextBasedService):
    def __init__(self, cloudshell_context, vcenter_context):
        self.cloudshell_context = cloudshell_context
        self.vcenter_context = vcenter_context

    def context_started(self):
        self.cloudshell_context.context_started()
        self.vcenter_context.context_started()

    def context_ended(self):
        self.cloudshell_context.context_ended()
        self.vcenter_context.context_ended()

    def get_objects(self):
        return self.cloudshell_context, self.vcenter_context


class CloudShellContextFactory(object):
    def create_context(self, context):
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


class CompositeContextFactory(object):
    def __init__(self, cloudshell_context_factory, vcenter_context_factory):
        """
        :type cloudshell_context_factory CloudShellContextFactory
        :param cloudshell_context_factory:
        :type vcenter_context_factory VCenterShellContextFactory
        :param vcenter_context_factory:
        :return:
        """
        self.cloudshell_context_factory = cloudshell_context_factory
        self.vcenter_context_factory = vcenter_context_factory

    def create_context(self, context):
        """

        :param context:
        :rtype CompositeContext
        :return:
        """
        cloudshell_context = self.cloudshell_context_factory.create_context(context)
        vsenter_context = self.vcenter_context_factory.create_context(cloudshell_context.create_session(), context)
        return CompositeContext(cloudshell_context, vsenter_context)
