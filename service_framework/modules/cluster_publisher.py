from service_framework.a_plugin import ThreadHandler as superClass
import time
import zmq


class Service(superClass):
    def initialize(self, module, stopevent):
        self.module = module
        self.stopevent = stopevent

        # subscribe to events of found RaspBoards when thier configuration
        # have been optained:
        found_event = '*'
        self.module.add_event_listener(found_event, self.publish)

        # init subscriber:
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        pub_url = 'tcp://%s:%s' % (self.module.ip_address,
                                   self.module.cluster_port)
        self.module.dispatch_event('LOG', (10, pub_url, config['service_name']))
        self.socket.bind(pub_url)

    def publish(self, event):
        event_type = event.type
        event_origin = event.origin_host
        event_data = str(event.data)
        if(event_origin == self.module.ip_address):
            self.socket.send('%s %s %s' % (event_type, event_origin, event_data))


config = {
    "service_name": "builtin/cluster_publisher",
    "handler": Service,
    "service_type": "thread",
    "service_category": "system",
    "dependencies": []
}
