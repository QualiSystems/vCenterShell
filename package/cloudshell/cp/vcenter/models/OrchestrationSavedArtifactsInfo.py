class OrchestrationSavedArtifactsInfo(object):
    def __init__(self, resource_name, created_date, restore_rules, saved_artifact):
        """
        :type resource_name: str
        :type created_date: date
        :type restore_rules: dict
        :type saved_artifact: OrchestrationSavedArtifact
        """
        self.resource_name = resource_name
        self.created_date = created_date
        self.restore_rules = restore_rules
        self.saved_artifact = saved_artifact
