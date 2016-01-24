from enum import Enum


class ActionTarget(object):
    def __init__(self):
        self.fullName = ''
        self.fullAddress = ''


class Action(object):
    def __init__(self):
        self.actionId = ''
        self.type = ''
        self.actionTarget = ActionTarget()


class BaseObject(object):
    def __init__(self):
        self.driverRequest = DriverRequest()
        self.driverResponse = DriverResponse()


class DriverRequest(object):
    def __init__(self):
        self.actions = []


class DriverResponse(object):
    def __init__(self):
        self.actionResults = []


class SetVlanParameters(object):
    def __init__(self):
        self.type = ''
        self.vlanIds = []
        self.mode = Mode.Access


class ConnectorAttribute(object):
    def __init__(self):
        self.type = ''
        self.attributeName = ''
        self.attributeValue = ''


class ActionResult(object):
    def __init__(self):
        self.type = ''
        self.actionId = ''
        self.infoMessage = ''
        self.errorMessage = ''
        self.success = ''


class SetVlanAction(Action):
    def __init__(self):
        super(SetVlanAction, self).__init__()
        self.conenctionId = ''
        self.connectionParams = SetVlanParameters()
        self.connectorAttributes = [ConnectorAttribute()]


class Mode(Enum):
    Trunk = 1,
    Access = 2
