from itertools import groupby
import sys, traceback

from cloudshell.cp.core.models import SaveApp, SaveAppResult

from cloudshell.cp.vcenter.common.utilites.savers.artifact_saver import ArtifactSaver, UnsupportedArtifactSaver
from cloudshell.cp.vcenter.common.vcenter.task_waiter import SynchronousTaskWaiter
from cloudshell.cp.vcenter.common.vcenter.vmomi_service import pyVmomiService


class SaveAppCommand:
    def __init__(self, pyvmomi_service, task_waiter, deployer, resource_model_parser, snapshot_saver):
        """
        :param pyvmomi_service:
        :type pyvmomi_service: pyVmomiService
        :param task_waiter: Waits for the task to be completed
        :type task_waiter:  SynchronousTaskWaiter
        """
        self.pyvmomi_service = pyvmomi_service
        self.task_waiter = task_waiter
        self.deployer = deployer
        self.resource_model_parser = resource_model_parser
        self.snapshot_saver = snapshot_saver

    def save_app(self, si, logger, vcenter_data_model, reservation_id, save_app_actions, cancellation_context):
        """
        Cretaes an artifact of an app, that can later be restored

        :param vcenter_data_model: VMwarevCenterResourceModel
        :param vim.ServiceInstance si: py_vmomi service instance
        :type si: vim.ServiceInstance
        :param logger: Logger
        :type logger: cloudshell.core.logger.qs_logger.get_qs_logger
        :param list[SaveApp] save_app_actions:
        :param cancellation_context:
        """
        results = []

        logger.info('Save apps command starting on ' + vcenter_data_model.default_datacenter)

        if not save_app_actions:
            raise Exception('Failed to save app, missing data in request.')

        actions_grouped_by_save_types = groupby(save_app_actions, lambda x: x.actionParams.savedType)
        artifactSaversToActions = {ArtifactSaver.factory(k,
                                                         self.pyvmomi_service,
                                                         vcenter_data_model,
                                                         si,
                                                         logger,
                                                         self.deployer,
                                                         reservation_id,
                                                         self.resource_model_parser,
                                                         self.snapshot_saver,
                                                         self.task_waiter): list(g)
                                   for k, g in actions_grouped_by_save_types}

        self.validate_requested_save_types_supported(artifactSaversToActions,
                                                     logger,
                                                     results)

        error_results = [r for r in results if not r.success]
        if not error_results:
            self.execute_save_actions_grouped_by_type(artifactSaversToActions,
                                                      cancellation_context,
                                                      logger,
                                                      results)

        return results

    def execute_save_actions_grouped_by_type(self, artifactSaversToActions, cancellation_context, logger, results):
        for artifactSaver in artifactSaversToActions.keys():
            save_actions = artifactSaversToActions[artifactSaver]
            for action in save_actions:
                try:
                    results.append(artifactSaver.save(save_action=action, cancellation_context=cancellation_context))
                except Exception:
                    ex_type, ex, tb = sys.exc_info()
                    results.append(SaveAppResult(action.actionId,
                                                 success=False,
                                                 errorMessage=ex.message,
                                                 infoMessage='\n'.join(traceback.format_exception(ex_type, ex, tb))))
                    logger.exception('Save app action {0} failed'.format(action.actionId))

    def validate_requested_save_types_supported(self, artifactSaversToActions, logger, results):
        unsupported_savers = [saver for saver in artifactSaversToActions.keys() if
                              isinstance(saver, UnsupportedArtifactSaver)]
        if unsupported_savers:
            error_message = "Unsupported save type was included in save app request: {0}" \
                .format(', '.join({saver.unsupported_save_type for saver in unsupported_savers}))

            logger.error(error_message)

            for artifactSaver in artifactSaversToActions.keys():
                save_actions = artifactSaversToActions[artifactSaver]
                for action in save_actions:
                    results.append(SaveAppResult(action.actionId,
                                                 success=False,
                                                 errorMessage=error_message))


