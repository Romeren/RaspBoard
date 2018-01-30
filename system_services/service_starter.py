from RaspBoard.a_service import RestHandler as superClass
import cPickle as pickle

class Service(superClass):
    def get(self):
        self.write('try post!')

    def post(self):
        print('START SERVICE')
        config = self.get_argument("config", None)
        auth = self.get_argument("authentication", None)
        if(auth is None or
           auth != self.module.cluster_authentication):
            print('auth', auth)
            return
        
        config = self.load_message(config)
        if('service_name' not in config or
           'handler' not in config or
           'service_type' not in config or
           'service_category' not in config):
            print('config', config)
            return
        print(config)
        handler = str(config['handler'])
        handler = pickle.loads(handler)
        config['handler'] = handler
        self.module.add_service(config)
        print("ending")
        self.write_error(200)



config = {
    "service_name": "builtin/service_starter",
    "handler": Service,
    "service_type": "rest",
    "service_category": "system",
    "dependencies": []
}
