# -*- coding: utf-8 -*-  # NOQA
from service_framework.a_plugin import ThreadHandler as abstract_plugin  # NOQA
from service_framework.events.event_module import Service_Changed_Event
from service_framework.events.event_module import Broker_Event


class Service(abstract_plugin):

    def initialize(self, module, stop_event):
        self.module = module
        self.stop_event = stop_event

        # add event listeners:
        self.module.event_dispatcher.add_event_listener( 
            Service_Changed_Event.ADDED, self.on_event
        )

        self.module.event_dispatcher.add_event_listener( 
            Service_Changed_Event.REMOVED, self.on_event
        )

        self.module.event_dispatcher.add_event_listener( 
            Service_Changed_Event.UPDATED, self.on_event
        )

        self.module.event_dispatcher.add_event_listener( 
            Service_Changed_Event.ERROR, self.on_event
        )

        self.module.event_dispatcher.add_event_listener( 
            Broker_Event.ERROR, self.on_event
        )

    def on_event(self, event):
        print('EVENT', event.type)
        print(event.data)




config = {"service_name": "log",
          "handler": Service,
          "service_type": "thread",
          "service_category": "core",
          "dependencies": [
               {'name': 'services', 'service': "*"}  # NOQA
              ]
          }
