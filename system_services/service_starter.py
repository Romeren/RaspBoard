from RaspBoard.a_service import RestHandler as superClass
import importlib as lib

class Service(superClass):
    def post(self):
        config = self.get_argument("config", None)
        auth = self.get_argument("authentication", None)
        if(auth is None or
           auth != self.module.cluster_authentication):
            return
        
        config = self.load_message(config)
        if('service_name' not in config or
           'module' not in config or
           'service_type' not in config or
           'service_category' not in config):
            return
        
        module_name = self.make_name(config)
        module = config['module']
        
        success = self.create_file(self.module.virtual_dir + module_name + '.py', module)
        if(not success):
            self.write('ERROR-Creating dir')
            return
        success, module = self.load_module(self.module.virtual_dir + module_name)
        if(not success):
            self.write('ERROR-Loading module')
            return

        self.module.add_service(module.config)


    def load_module(self, file_name):
        m = None
        try:
            m = lib.import_module(file_name.replace('/', '.'))
        except Exception as e:
            print(e)
            return False, m
        return True, m

    def create_file(self, file_name, content):
        try:
            file = open(file_name, 'w+')
            file.write(content)
            file.close()
        except Exception as e:
            print(e)
            return False
        return True

    def make_name(self, config):
        return "/%s_%s_%s" % (config['service_type'], config['service_category'], config['service_name'].replace('/', '_'))

config = {
    "service_name": "builtin/service_starter",
    "handler": Service,
    "service_type": "rest",
    "service_category": "system",
    "dependencies": []
}
