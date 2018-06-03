from cloudshell.cp.vcenter.common.utilites.savers.linked_clone_artifact_saver import LinkedCloneArtifactSaver


class ArtifactSaver(object):
    @staticmethod
    def factory(saveDeploymentModel, pv_service, vcenter_data_model, si, logger, deployer, reservation_id,
                resource_model_parser, snapshot_saver, task_waiter):
        if saveDeploymentModel == 'VCenter Deploy VM From Linked Clone':
            return LinkedCloneArtifactSaver(pv_service, vcenter_data_model, si, logger, deployer, reservation_id,
                                            resource_model_parser, snapshot_saver, task_waiter)
        return UnsupportedArtifactSaver(saveDeploymentModel)


class UnsupportedArtifactSaver(object):
    def __init__(self, saveDeploymentModel):
        self.unsupported_save_type = saveDeploymentModel
