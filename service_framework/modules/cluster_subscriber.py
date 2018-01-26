from service_framework.a_plugin import ThreadHandler as superClass
from service_framework.events.event_module import Event as frameworkEvent
import zmq


class Service(superClass):
    def initialize(self, module, stopevent):
        self.module = module
        self.stopevent = stopevent

        # subscribe to events of found RaspBoards when thier configuration
        # have been optained:
        found_event = 'SERVICE_CONTAINER_CONFIGURATION_OPTAINED'
        self.module.add_event_listener(found_event, self.subscribe)

        # init subscriber:
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        topFilter = ""
        self.socket.setsockopt(zmq.SUBSCRIBE, topFilter)

        self.recieve_msg()

    def subscribe(self, event):
        ip_address = self.try_get(event.data, 'ip_address')
        port = self.try_get(event.data, 'cluster_port')

        if(port is None or ip_address is None):
            return

        sub_url = 'tcp://%s:%s' % (ip_address, port)
        self.socket.connect(sub_url)
        self.module.dispatch_event('SUBSCRIBED_TO_CONTAINER',
                                   (sub_url, config['service_name']))

    def recieve_msg(self):
        while(not self.stopevent.is_set()):
            msg = self.socket.recv()
            
            isSuccess, event = self.parse_msg_to_event(msg)
            if(isSuccess):
                self.module.event_dispatcher.dispatch_event(event)
            else:
                self.module.dispatch_event('LOG', (4, 'FAILED TO PARSE MSG', event, config['service_name']))

    def parse_msg_to_event(self, msg):
        try:
            e_t, e_org, e_d = msg.split(' ', 2)
            
            try:
                e_d = self.load_message(e_d)
            except:
                return False, e_d

            event = frameworkEvent(e_t, e_org, e_d)
            return True, event
        except:
            return False, msg


    def try_get(self, obj, field, default=None):
        if(field in obj):
            return obj[field]
        else:
            return default

config = {
    "service_name": "builtin/cluster_subscriber",
    "handler": Service,
    "service_type": "thread",
    "service_category": "system",
    "dependencies": [
    ]
}
