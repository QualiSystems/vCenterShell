import jsonpickle
from common.cloudshell.connectivity_schema import DriverRequest


class BulkRequestBuilder(object):

    def __init__(self):
        self.actions = []

    def append_action(self, action):
        self.actions.append(action)

    def get_request(self):
        driver_request = DriverRequest()
        driver_request.actions = self.actions
        return jsonpickle.encode(driver_request, unpicklable=False)


