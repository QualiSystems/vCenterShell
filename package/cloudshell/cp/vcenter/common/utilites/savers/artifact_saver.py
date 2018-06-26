from cloudshell.cp.vcenter.common.utilites.savers.linked_clone_artifact_saver import LinkedCloneArtifactHandler


class ArtifactHandler(object):
    @staticmethod
    def factory(saveDeploymentModel, pv_service, vcenter_data_model, si, logger, deployer, reservation_id,
                resource_model_parser, snapshot_saver, task_waiter, folder_manager, port_configurer):
        if saveDeploymentModel == 'VCenter Deploy VM From Linked Clone':
            return LinkedCloneArtifactHandler(pv_service, vcenter_data_model, si, logger, deployer, reservation_id,
                                              resource_model_parser, snapshot_saver, task_waiter, folder_manager,
                                              port_configurer)
        return UnsupportedArtifactHandler(saveDeploymentModel)


class UnsupportedArtifactHandler(object):
    def __init__(self, saveDeploymentModel):
        self.unsupported_save_type = saveDeploymentModel
