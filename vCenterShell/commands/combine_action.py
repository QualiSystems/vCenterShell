class CombineAction(object):
    @staticmethod
    def combine(action, action_to_combine):
        method_name = '_' + action.type
        if hasattr(CombineAction, method_name):
            return getattr(CombineAction, method_name)(action, action_to_combine)
        raise ValueError('Action type {0} is not supported'.format(action.type))

    @staticmethod
    def _setVlan(action, action_to_combine):
        action.connectionParams.vlanIds += action_to_combine.connectionParams.vlanIds
        return action

    @staticmethod
    def _removeVlan(action, action_to_combine):
        action.connectorAttributes += action_to_combine.connectorAttributes
        return action

