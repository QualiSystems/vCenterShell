class Test(object):
    pass

class ActionResult(object):

    def __init__(self):
        self.actionId = '',
        self.type = '',
        self.infoMessage = '',
        self.errorMessage = '',
        self.success = True,
        self.updatedInterface = ''


class CustomActionResult(ActionResult):
    def __init__(self):
        super(CustomActionResult, self).__init__()
        self.network_name = ''

    def get_base_class(self):
        action = ActionResult()
        for att in self._get_attributes_names(action):
            if hasattr(self, att):
                value = str(getattr(self, att))
                setattr(action, att, value)

        return action

    @staticmethod
    def _get_attributes_names(cls):
        return (attr for attr in dir(cls) if not attr.startswith("__"))
