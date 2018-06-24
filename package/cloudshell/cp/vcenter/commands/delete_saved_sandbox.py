import copy
from itertools import groupby

from cloudshell.cp.core.models import ActionResultBase

from cloudshell.cp.vcenter.common.utilites.savers.artifact_saver import ArtifactHandler, UnsupportedArtifactHandler
from cloudshell.cp.vcenter.common.vcenter.task_waiter import SynchronousTaskWaiter
from cloudshell.cp.vcenter.common.vcenter.vmomi_service import pyVmomiService

import os
from multiprocessing.pool import ThreadPool


class DeleteSavedSandboxCommand:
    def __init__(self, pyvmomi_service, task_waiter, deployer, resource_model_parser, snapshot_saver, folder_manager,
                 cancellation_service, port_group_configurer):
        """
        :param pyvmomi_service:
        :type pyvmomi_service: pyVmomiService
        :param task_waiter: Waits for the task to be completed
        :param folder_manager: cloudshell.cp.vcenter.common.vcenter.folder_manager.FolderManager
        :type task_waiter:  SynchronousTaskWaiter
        """
        self.pyvmomi_service = pyvmomi_service
        self.task_waiter = task_waiter
        self.deployer = deployer
        self.resource_model_parser = resource_model_parser
        self.snapshot_saver = snapshot_saver
        self.folder_manager = folder_manager
        SAVE_APPS_THREAD_POOL_SIZE = int(os.getenv('SaveAppsThreadPoolSize', 10))
        self._pool = ThreadPool(SAVE_APPS_THREAD_POOL_SIZE)
        self.cs = cancellation_service
        self.pg = port_group_configurer

    def delete_sandbox(self, si, logger, vcenter_data_model, delete_sandbox_actions, cancellation_context):
        """
        Cretaes an artifact of an app, that can later be restored

        :param vcenter_data_model: VMwarevCenterResourceModel
        :param vim.ServiceInstance si: py_vmomi service instance
        :type si: vim.ServiceInstance
        :param logger: Logger
        :type logger: cloudshell.core.logger.qs_logger.get_qs_logger
        :param list[SaveApp] delete_sandbox_actions:
        :param cancellation_context:
        """
        results = []

        logger.info('Save apps command starting on ' + vcenter_data_model.default_datacenter)

        if not delete_sandbox_actions:
            raise Exception('Failed to save app, missing data in request.')

        actions_grouped_by_save_types = groupby(delete_sandbox_actions, lambda x: x.actionParams.saveDeploymentModel)
        artifactHandlersToActions = {ArtifactHandler.factory(k,
                                                             self.pyvmomi_service,
                                                             vcenter_data_model,
                                                             si,
                                                             logger,
                                                             self.deployer,
                                                             None,
                                                             self.resource_model_parser,
                                                             self.snapshot_saver,
                                                             self.task_waiter,
                                                             self.folder_manager,
                                                             self.pg): list(g)
                                     for k, g in actions_grouped_by_save_types}

        if not next((a for a in artifactHandlersToActions.keys() if isinstance(a, UnsupportedArtifactHandler)), None):
            return
        error_results = [r for r in results if not r.success]
        if not error_results:
            results = self._execute_delete_saved_sandbox(artifactHandlersToActions,
                                                         cancellation_context,
                                                         logger,
                                                         results)

        return results

    def _execute_delete_saved_sandbox(self, artifactHandlersToActions, cancellation_context, logger, results):
        for artifactHandler in artifactHandlersToActions.keys():
            delete_sandbox_results = artifactHandler.delete(artifactHandlersToActions[artifactHandler], cancellation_context)
            results.extend(delete_sandbox_results)
        return results

    def _destroy(self, (artifactSaver, action)):
        artifactSaver.destroy(save_action=action)
        return ActionResultBase(action.actionId,
                                success=False,
                                errorMessage='Save app action {0} was cancelled'.format(action.actionId),
                                infoMessage='')

    def _validate_supported_artifact_handlers(self, artifactHandlersToActions, logger, results):
        unsupported_handlers = [saver for saver in artifactHandlersToActions.keys() if
                                isinstance(saver, UnsupportedArtifactHandler)]
        if unsupported_handlers:
            log_error_message = "Unsupported save type was included in delete saved app request: {0}" \
                .format(', '.join({saver.unsupported_save_type for saver in unsupported_handlers}))
            logger.error(log_error_message)

            for artifact_handler in artifactHandlersToActions.keys():
                if artifact_handler in unsupported_handlers:
                    result_error_message = 'Unsupported save type ' + artifact_handler.unsupported_save_type
                else:
                    result_error_message = ''

                delete_saved_app_actions = artifactHandlersToActions[artifact_handler]
                for action in delete_saved_app_actions:
                    results.append(ActionResultBase(action.actionId,
                                                    success=False,
                                                    errorMessage=result_error_message))
