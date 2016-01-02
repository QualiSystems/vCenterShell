import os
import uuid

class CommandContextMocker:

    def __init__(self):
        pass

    @staticmethod
    def set_vm_uuid_param(name):
        vm_uuid = str(uuid.uuid4())
        CommandContextMocker.set_command_param(name,vm_uuid)
        return uuid

    @staticmethod
    def set_command_param(name, value):
        os.environ[name]= value
