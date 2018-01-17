# -*- coding: utf-8 -*-  # NOQA
""" Wrapper for implementations of plugins!
handles subscriping to server and sending heartbeats.
"""

from service_framework.events.event_module import EventDispatcher as dispatcher
from service_framework.events.event_module import named_events as event_map

from service_framework.service_container.event_subscriber import Event_Subscriber
from service_framework.service_container.service_register import service_register
from service_framework.service_container.Container import Container

import atexit
import signal
import time

from threading import Event
from threading import Thread
import zmq


class Controller(object):

    def __init__(self, settings={}):
        self.is_exiting = False
        self.stop_event = Event()
        self.setup_termination_handlers()

        self.address = util.get_own_ipaddress()
        self.port = 5555
                
        self.service_register = service_register()
        self.event_dispatcher = None
        self.event_subscriber = None
        
        self.start_event_subscriber()
        self.__add_event_listeners()

        self.container = Container()

    def start_event_subscriber(self):
        self.event_dispatcher = dispatcher()
        self.event_subscriber = Event_Subscriber(self.event_dispatcher)
        subscriber = Thread(target=self.event_subscriber.subscribe,
                            args=(self.address, self.port+1, self.stop_event))
        subscriber.start()

    def __add_event_listeners(self):
        self.event_dispatcher.add_event_listener(event_map.START_PLUGIN, self.onAddServiceToContainer)
        self.event_dispatcher.add_event_listener(event_map.STOP_PLUGIN, self.onRemoveServiceFromContainer)
        self.event_dispatcher.add_event_listener(event_map.REMOTE_SERVICE_ADDED, self.onServiceAdded)
        self.event_dispatcher.add_event_listener(event_map.REMOTE_SERVICE_REMOVED, self.onServiceRemoved)

    
    # --------------------------------------------------------
    # Event handlers
    # --------------------------------------------------------
    def onApplicationSecretChanged(self, event):
        self.settings["cookie_secret"] = event.data

    def onAddServiceToContainer(self, event):
        pass
        # serviceCode = event.data['code']
        # serviceModule = imp.new_module(serviceCode)
        # if('config' not in serviceModule):
        #     return
        
        # serviceConfig = serviceModule.config

    def onRemoveServiceFromContainer(self, event):
        pass



    def onServiceRemoved(self, event):
        self.service_register.remove_service(event.data)
    
    def onServiceAdded(self, event):
        self.service_register.add_service(event.data['topic'], event.data["service"])
    
    # --------------------------------------------------------
    # Exit and termination handlers:
    # --------------------------------------------------------
    def setup_termination_handlers(self):
        #  Add exit handler:
        atexit.register(self.termination_handler)
        #  add interrupt handler
        signal.signal(signal.SIGINT, self.exit_handler)

    def termination_handler(self):
        print("Terminating...")
        # unsubscripe from broker:
        self.subscribe_to_broker(isSubscribing=False)

        # stop all threads
        self.stop_event.set()
        time.sleep(1)
        # stop tornado:
        if(self.is_exiting):
            ioloop.IOLoop.instance().stop()
            self.is_exiting = False

    def exit_handler(self, signal, frame):
        print("INTERRUPTED! -terminating")

        # stop all threads
        self.stop_event.set()
        time.sleep(1)
        # stop tornado:
        if(self.is_exiting):
            ioloop.IOLoop.instance().stop()
            self.is_exiting = False
        exit()

