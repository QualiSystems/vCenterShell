import copy
import threading
from itertools import groupby
import sys, traceback

from cloudshell.cp.core.models import SaveApp, SaveAppResult

from cloudshell.cp.vcenter.common.utilites.savers.artifact_saver import ArtifactHandler, UnsupportedArtifactHandler
from cloudshell.cp.vcenter.common.vcenter.task_waiter import SynchronousTaskWaiter
from cloudshell.cp.vcenter.common.vcenter.vmomi_service import pyVmomiService

import os
from multiprocessing.pool import ThreadPool


class SaveAppCommand:
    def __init__(self, pyvmomi_service, task_waiter, deployer, resource_model_parser, snapshot_saver, folder_manager,
                 cancellation_service, port_group_configurer):
        """
        :param pyvmomi_service:
        :type pyvmomi_service: pyVmomiService
        :param task_waiter: Waits for the task to be completed
        :param folder_manager: cloudshell.cp.vcenter.common.vcenter.folder_manager.FolderManager
        :type task_waiter:  SynchronousTaskWaiter
        :param port_group_configurer: VirtualMachinePortGroupConfigurer
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
        self.port_group_configurer = port_group_configurer

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

        logger.info('Save Sandbox command starting on ' + vcenter_data_model.default_datacenter)

        if not save_app_actions:
            raise Exception('Failed to save app, missing data in request.')

        actions_grouped_by_save_types = groupby(save_app_actions, lambda x: x.actionParams.saveDeploymentModel)
        # artifactSaver or artifactHandler are different ways to save artifacts. For example, currently
        # we clone a vm, thenk take a snapshot. restore will be to deploy from linked snapshot
        # a future artifact handler we might develop is save vm to OVF file and restore from file.
        artifactSaversToActions = {ArtifactHandler.factory(k,
                                                           self.pyvmomi_service,
                                                           vcenter_data_model,
                                                           si,
                                                           logger,
                                                           self.deployer,
                                                           reservation_id,
                                                           self.resource_model_parser,
                                                           self.snapshot_saver,
                                                           self.task_waiter,
                                                           self.folder_manager,
                                                           self.port_group_configurer,
                                                           self.cs)
                                   : list(g)
                                   for k, g in actions_grouped_by_save_types}

        self.validate_requested_save_types_supported(artifactSaversToActions,
                                                     logger,
                                                     results)

        error_results = [r for r in results if not r.success]
        if not error_results:
            logger.info('Handling Save App requests')
            results = self._execute_save_actions_using_pool(artifactSaversToActions,
                                                            cancellation_context,
                                                            logger,
                                                            results)
            logger.info('Completed Save Sandbox command')
        else:
            logger.error('Some save app requests were not valid, Save Sandbox command failed.')
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

        if self.cs.check_if_cancelled(cancellation_context):
            raise Exception('Save sandbox was cancelled')

        results_before_deploy = copy.deepcopy(results)

        results.extend(self._pool.map(self._save, save_params))

        operation_error = next((a for a in results if not a.success), False)

        thread_id = threading.current_thread().ident

        if self.cs.check_if_cancelled(cancellation_context):
            logger.info('[{0}] Save sandbox was cancelled, rolling back saved apps'.format(thread_id))
            results = self._rollback(destroy_params, logger, results, results_before_deploy, thread_id)

        elif operation_error:
            logger.error('[{0}] Save Sandbox operation failed, rolling backed saved apps. See logs for more information'.format(thread_id))
            results = self._rollback(destroy_params, logger, results, results_before_deploy, thread_id)

        return results

    def _rollback(self, destroy_params, logger, results, results_before_deploy, thread_id):
        results = results_before_deploy
        for param in destroy_params:
            results.append(self._destroy(param))
            logger.info('[{0}] Save Sandbox roll back completed'.format(thread_id))
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
                             errorMessage='Save app action {0} was rolled back'.format(action.actionId),
                             infoMessage='')

    def validate_requested_save_types_supported(self, artifactSaversToActions, logger, results):
        unsupported_savers = [saver for saver in artifactSaversToActions.keys() if
                              isinstance(saver, UnsupportedArtifactHandler)]
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

