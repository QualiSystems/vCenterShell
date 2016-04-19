from cloudshell.api.cloudshell_api import CloudShellAPISession


class CloudShellSessionFactory(object):

    @staticmethod
    def create_session(context):
        """
        Creates session with interaction with CloudShell
        :param context: instance of ResourceCommandContext or AutoLoadCommandContext
        :type context: cloudshell.shell.core.context.ResourceCommandContext
        """
        # noinspection PyTypeChecker
        session = CloudShellAPISession(host=context.connectivity.server_address,
                                       token_id=context.connectivity.admin_auth_token,
                                       username=None,
                                       password=None,
                                       domain=CloudShellSessionFactory._get_domain(context))
        return session

    @staticmethod
    def _get_domain(context):
        # noinspection PyBroadException
        try:
            return context.remote_reservation.domain
        except:
            return context.reservation.domain

