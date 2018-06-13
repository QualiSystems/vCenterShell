import copy
from itertools import groupby
import sys, traceback

from cloudshell.cp.core.models import SaveApp, SaveAppResult

from cloudshell.cp.vcenter.common.utilites.savers.artifact_saver import ArtifactSaver, UnsupportedArtifactSaver
from cloudshell.cp.vcenter.common.vcenter.task_waiter import SynchronousTaskWaiter
from cloudshell.cp.vcenter.common.vcenter.vmomi_service import pyVmomiService

import os
from multiprocessing.pool import ThreadPool


class SaveAppCommand:
    def __init__(self, pyvmomi_service, task_waiter, deployer, resource_model_parser, snapshot_saver, folder_manager):
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

        actions_grouped_by_save_types = groupby(save_app_actions, lambda x: x.actionParams.saveDeploymentModel)
        artifactSaversToActions = {ArtifactSaver.factory(k,
                                                         self.pyvmomi_service,
                                                         vcenter_data_model,
                                                         si,
                                                         logger,
                                                         self.deployer,
                                                         reservation_id,
                                                         self.resource_model_parser,
                                                         self.snapshot_saver,
                                                         self.task_waiter,
                                                         self.folder_manager): list(g)
                                   for k, g in actions_grouped_by_save_types}

        self.validate_requested_save_types_supported(artifactSaversToActions,
                                                     logger,
                                                     results)

        error_results = [r for r in results if not r.success]
        if not error_results:
            self._execute_save_actions_using_pool(artifactSaversToActions,
                                                  cancellation_context,
                                                  logger,
                                                  results)

        return results

    def _execute_save_actions_using_pool(self, artifactSaversToActions, cancellation_context, logger, results):
        save_params = []
        destroy_params = []

        for artifactSaver in artifactSaversToActions.keys():
            save_params.extend(self._get_save_params(artifactSaver,
                                                     artifactSaversToActions,
                                                     cancellation_context,
                                                     logger))
            destroy_params.extend(self._get_destroy_params(artifactSaver, artifactSaversToActions))

        if cancellation_context.is_cancelled:
            raise Exception('Save sandbox was cancelled')

        results_before_deploy = copy.deepcopy(results)

        results.extend(self._pool.map(self._save, save_params))

        if cancellation_context.is_cancelled:
            results = results_before_deploy
            for param in destroy_params:
                results.append(self._destroy(param))

        return results

    def _get_save_params(self, artifactSaver, artifactSaversToActions, cancellation_context, logger):
        return [(artifactSaver, a, cancellation_context, logger) for a in artifactSaversToActions[artifactSaver]]

    def _get_destroy_params(self, artifactSaver, artifactSaversToActions):
        return [(artifactSaver, a) for a in artifactSaversToActions[artifactSaver]]

    def _save(self, (artifactSaver, action, cancellation_context, logger)):
        try:
            return artifactSaver.save(save_action=action, cancellation_context=cancellation_context)
        except Exception:
            ex_type, ex, tb = sys.exc_info()
            logger.exception('Save app action {0} failed'.format(action.actionId))
            return SaveAppResult(action.actionId,
                                 success=False,
                                 errorMessage=ex.message,
                                 infoMessage='\n'.join(traceback.format_exception(ex_type, ex, tb)))

    def _destroy(self, (artifactSaver, action)):
        artifactSaver.destroy(save_action=action)
        return SaveAppResult(action.actionId,
                             success=False,
                             errorMessage='Save app action {0} was cancelled'.format(action.actionId),
                             infoMessage='')

    def validate_requested_save_types_supported(self, artifactSaversToActions, logger, results):
        unsupported_savers = [saver for saver in artifactSaversToActions.keys() if
                              isinstance(saver, UnsupportedArtifactSaver)]
        if unsupported_savers:
            log_error_message = "Unsupported save type was included in save app request: {0}" \
                .format(', '.join({saver.unsupported_save_type for saver in unsupported_savers}))
            logger.error(log_error_message)

            for artifactSaver in artifactSaversToActions.keys():
                if artifactSaver in unsupported_savers:
                    result_error_message = 'Unsupported save type ' + artifactSaver.unsupported_save_type
                else:
                    result_error_message = ''

                save_actions = artifactSaversToActions[artifactSaver]
                for action in save_actions:
                    results.append(SaveAppResult(action.actionId,
                                                 success=False,
                                                 errorMessage=result_error_message))


def _get_async_results(async_results, thread_pool):
    thread_pool.close()
    thread_pool.join()
    results = []
    for async_result in async_results:
        save_result = async_result.get()
        results.append(save_result)
    return results
