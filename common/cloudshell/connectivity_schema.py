class DriverRequest(object):
    def __init__(self):
        self.actions = []


class Action(object):
    def __init__(self):
        self.actionId = ''
        self.type = ''
        self.actionTarget = {}
        self.conenctionId = ''
        self.connectionParams = {}
        self.connectorAttributes = [{}]


