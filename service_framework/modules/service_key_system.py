from service_framework.a_plugin import ThreadHandler as superClass
import time
import random
import os
import string


class Key():
    def __init__(self, name, length, key_type, shouldUpdate):
        self.name=name
        self.length = length
        self.key_type = key_type
        self.shouldUpdate = shouldUpdate
        self.key = None
        self.update_key()

    def update_key(self):
        if(self.key_type == 'CHARS'):
            self.key = self.gen_char_key(self.length)
        elif(self.key_type == 'BYTES'):
            self.key = self.gen_byte_key(self.length)
    
    def gen_byte_key(self, length):
        return os.urandom(length)

    def gen_char_key(self,length):
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))



class Service(superClass):
    def initialize(self, module, stopevent):
        self.module = module
        self.stopevent = stopevent

        self.keys = {}
        self.keys_for_update = []
        self.update_interval = 10

        self.module.add_event_listener('SYSTEM_CREATE_KEY', self.create_key)
        self.module.add_event_listener('SYSTEM_UPDATE_KEY', self.update_key)

    def update_key(self, event):
        key_name, new_key = event.data
        k = self.keys[key_name]
        k.key = new_key
        self.module.dispatch_event(key_name.upper() + '_KEY_CHANGED', (k.key))

    def create_key(self, event):
        key_name, key_length, key_type, shouldUpdate = event.data
        
        key = None
        if(key_name not in self.keys):
            key = Key(key_name, key_length, key_type, shouldUpdate)
            self.keys[key_name] = key
            if(shouldUpdate and key_name not in self.keys_for_update):
                self.keys_for_update.append(key_name)
        else:
            key = self.keys[key_name]

        self.module.dispatch_event(key_name.upper() + '_KEY_CHANGED', (key.key))

config = {
    "service_name": "builtin/service_key_system",
    "handler": Service,
    "service_type": "thread",
    "service_category": "system",
    "dependencies": []
}
