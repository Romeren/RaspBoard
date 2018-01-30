from RaspBoard.a_service import ThreadHandler as superClass
import importlib as lib
import os

class Service(superClass):
    def initialize(self, module, stopevent):
        files = os.listdir(module.virtual_dir)
        for f in files:
            if(f.endswith('.py') and not f == '__init__.py'):
                m = lib.import_module(module.virtual_dir.replace('/', '.') + '.' + f.replace('.py', ''))
                if(hasattr(m, 'config')):
                    module.add_service(m.config)


config = {
    "service_name": "builtin/load_services",
    "handler": Service,
    "service_type": "thread",
    "service_category": "system",
    "dependencies": []
}
