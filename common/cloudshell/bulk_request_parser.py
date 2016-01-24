import jsonpickle


class BulkRequestParser(object):
    def __init__(self):
        pass

    def parse(self, request):
        jsonpickle.decode(request)

