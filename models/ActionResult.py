
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
        return super(CustomActionResult, self)

