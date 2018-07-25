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
        DELETE_SAVED_APPS_THREAD_POOL_SIZE = int(os.getenv('DeleteSavedAppsThreadPoolSize', 10))
        self._pool = ThreadPool(DELETE_SAVED_APPS_THREAD_POOL_SIZE)
        self.cs = cancellation_service
        self.pg = port_group_configurer

    def delete_sandbox(self, si, logger, vcenter_data_model, delete_sandbox_actions, cancellation_context):
        """
        Deletes a saved sandbox's artifacts

        :param vcenter_data_model: VMwarevCenterResourceModel
        :param vim.ServiceInstance si: py_vmomi service instance
        :type si: vim.ServiceInstance
        :param logger: Logger
        :type logger: cloudshell.core.logger.qs_logger.get_qs_logger
        :param list[SaveApp] delete_sandbox_actions:
        :param cancellation_context:
        """
        results = []

        logger.info('Deleting saved sandbox command starting on ' + vcenter_data_model.default_datacenter)

        if not delete_sandbox_actions:
            raise Exception('Failed to delete saved sandbox, missing data in request.')

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
                                                             self.pg,
                                                             self.cs): list(g)
                                     for k, g in actions_grouped_by_save_types}

        self._validate_save_deployment_models(artifactHandlersToActions, delete_sandbox_actions, results)

        error_results = [r for r in results if not r.success]
        if not error_results:
            results = self._execute_delete_saved_sandbox(artifactHandlersToActions,
                                                         cancellation_context,
                                                         logger,
                                                         results)

        return results

    def _validate_save_deployment_models(self, artifactHandlersToActions, delete_sandbox_actions, results):
        unsupported_save_deployment_models = [a.unsupported_save_type for a in artifactHandlersToActions.keys() if
                                              isinstance(a, UnsupportedArtifactHandler)]
        if unsupported_save_deployment_models:
            for action in delete_sandbox_actions:
                unsupported_msg = 'Unsupported save deployment models: {0}'.format(
                    ', '.join(unsupported_save_deployment_models))
                results.append(
                    ActionResultBase(type='DeleteSavedAppResult',
                                     actionId=action.actionId,
                                     success=False,
                                     infoMessage=unsupported_msg,
                                     errorMessage=unsupported_msg)
                )

    def _execute_delete_saved_sandbox(self, artifactHandlersToActions, cancellation_context, logger, results):
        for artifactHandler in artifactHandlersToActions.keys():
            delete_sandbox_results = artifactHandler.delete(artifactHandlersToActions[artifactHandler],
                                                            cancellation_context,
                                                            self._pool)
            results.extend(delete_sandbox_results)
        return results

