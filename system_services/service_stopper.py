from RaspBoard.a_service import RestHandler as superClass

class Service(superClass):
    
    def post(self):
        topic = self.get_argument("topic", None)
        auth = self.get_argument("authentication", None)
        if(topic is None or
           auth is None or
           auth != self.module.cluster_authentication):
            return
        self.module.remove_services(topic)

config = {
    "service_name": "builtin/service_stopper",
    "handler": Service,
    "service_type": "rest",
    "service_category": "system",
    "dependencies": []
}
