from service_framework.a_plugin import ThreadHandler as superClass
import pyaes
import time
import zmq


class Service(superClass):
    def initialize(self, module, stopevent):
        self.module = module
        self.stopevent = stopevent

        self.pub_sub_encryption_key = None
        self.key_name = 'PUBSUB'
        self.key_length = 32
        self.key_type = 'BYTES'
        self.shouldUpdate = True
        self.key_change_event_name = self.key_name + '_KEY_CHANGED'
        self.create_key_name = 'SYSTEM_CREATE_KEY'
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
        
        event_data = self.dump_message(event.data)
        if(event_data is None):
            event_data = event.data

        if(self.pub_sub_encryption_key == None and event_type != self.create_key_name and event_type != self.key_change_event_name):
            self.module.dispatch_event(self.create_key_name, (self.key_name, self.key_length, self.key_type, self.shouldUpdate))

        if(event_origin == self.module.ip_address):
            message = '%s %s %s' % (event_type, event_origin, event_data)
            if(self.pub_sub_encryption_key is not None):
                aes = pyaes.AESModeOfOperationCTR(self.pub_sub_encryption_key)
                message = aes.encrypt(message)
            self.socket.send_multipart(message)

        if(self.key_change_event_name == event_type):
            self.pub_sub_encryption_key = event.data


config = {
    "service_name": "builtin/cluster_publisher",
    "handler": Service,
    "service_type": "thread",
    "service_category": "system",
    "dependencies": []
}
