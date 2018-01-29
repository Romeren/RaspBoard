from service_framework.common.a_plugin import ThreadHandler as superClass
import zmq


class Service(superClass):
    def initialize(self, module, stopevent):
        self.module = module
        self.stopevent = stopevent

        raw_input('--ENTER--')
        self.module.exit_handler(None, None)


config = {
    "service_name": "builtin/killer",
    "handler": Service,
    "service_type": "thread",
    "service_category": "system",
    "dependencies": [
    ]
}
