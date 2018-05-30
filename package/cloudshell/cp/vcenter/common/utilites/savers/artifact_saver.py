from cloudshell.cp.vcenter.common.utilites.savers.linked_clone_artifact_saver import LinkedCloneArtifactSaver


class ArtifactSaver(object):
    @staticmethod
    def factory(savedType, pv_service, vcenter_data_model, si, logger, deployer, reservation_id,
                resource_model_parser, snapshot_saver, task_waiter):
        if savedType == 'linkedClone':
            return LinkedCloneArtifactSaver(pv_service, vcenter_data_model, si, logger, deployer, reservation_id,
                                            resource_model_parser, snapshot_saver, task_waiter)
        raise Exception('Artifact save type not supported')