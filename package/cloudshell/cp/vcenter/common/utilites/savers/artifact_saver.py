from cloudshell.cp.vcenter.common.utilites.savers.linked_clone_artifact_saver import LinkedCloneArtifactSaver


class ArtifactSaver(object):
    @staticmethod
    def factory(savedType, pv_service, vcenter_data_model, si, logger, deployer, reservation_id,
                resource_model_parser, snapshot_saver, task_waiter):
        if savedType == 'linkedClone':
            return LinkedCloneArtifactSaver(pv_service, vcenter_data_model, si, logger, deployer, reservation_id,
                                            resource_model_parser, snapshot_saver, task_waiter)
        return UnsupportedArtifactSaver(savedType)

class UnsupportedArtifactSaver(object):
    def __init__(self, saved_type):
        self.unsupported_save_type = saved_type
