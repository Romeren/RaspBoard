import atexit  # NOQA
from tornado import web, ioloop
import random as rnd
from RaspBoard.common import utilities as util
from RaspBoard.common_modules import ui_modules as uim
from RaspBoard.common.event_module import Event as frameworkEvent
from RaspBoard.common.event_module import EventDispatcher as dispatcher
from RaspBoard.common.service_register import service_register
import RaspBoard.common.read_file as read_file
import signal
import string
import sys
import os
import uuid
from threading import Event
from threading import Thread
import time


class Container(object):
    """docstring for Container"""

    def __init__(self, settings={}):
        read_file.create_dir('virtual_dir')
        chars = string.ascii_letters + string.digits
        application_secret = ''.join(rnd.choice(chars) for _ in range(50))
        cookie_secret = ''.join(rnd.choice(chars) for _ in range(50))
        cluster_authentication = ''.join(rnd.choice(chars) for _ in range(255))


        self.raspboard_id = self.get_fieldordefault(settings, 'raspboard_id', str(uuid.uuid4()))
        self.settings = settings
        # Debug and logging
        self.log_level = self.get_fieldordefault(settings, 'LOG_LEVEL', 0)

        # Safty and security
        self.cluster_authentication = self.get_fieldordefault(settings, 'cluster_authentication', cluster_authentication)  # NOQA
        self.application_secret = self.get_fieldordefault(settings, 'application_secret', application_secret)  # NOQA
        self.cookie_secret = self.get_fieldordefault(settings, 'cookie_secret', cookie_secret)  # NOQA
        self.settings["cookie_secret"] = self.cookie_secret

        # Network configuration:
        self.port = self.get_fieldordefault(settings, 'port', 80)                          # Port for accessing webserver
        self.discovery_port = self.get_fieldordefault(settings, 'discovery_port', 9999)    # Port for discovering services
        self.cluster_port = self.get_fieldordefault(settings, 'cluster_port', 9998)        # Port for cluster network
        self.ip_address = util.get_own_ipaddress()

        # Event System:
        self.event_dispatcher = dispatcher()

        # Services configuration:
        self.app = None
        self.service_register = service_register(self)
        # Running Threads:
        self.threads = {}
        self.stop_event = Event()  # Safely stopping services on exits:
        self.is_exiting = True  # Safely stopping services on exits:

        # Add exit handler:
        atexit.register(self.termination_handler)
        signal.signal(signal.SIGINT, self.exit_handler)

        self.__setup_default_settings__()

        t = Thread(target=self.start_webserver)
        t.daemon = True
        t.start()
        time.sleep(2)

    def start_webserver(self):
        # add listener to port:
        self.app = web.Application([], **self.settings)
        self.app.listen(self.port)
        ioloop.IOLoop.instance().start()

    def remove_services(self, topic):
        services = self.service_register.get_services(topic)
        removed = []
        for config in services:
            service_topic = self.service_register.build_topic(config)
            if(config is None):
                continue
        
            if(config['host_address'] != self.ip_address or
               config['port'] != self.port):
               continue
            
            if('handler' not in config):
                continue

            if(config['service_type'] == 'thread'):
                t, stop_event = self.threads.pop(service_topic, None)
                stop_event.set()
                removed.append(service_topic)
            elif(config['service_type'] == 'rest'):
                handlers_to_remove = []
                for tuble in self.app.handlers:
                    x = tuble[1][0]
                    if(x.handler_class == config['handler']):
                        handlers_to_remove.append(tuble)
                for h in handlers_to_remove:
                    self.app.handlers.remove(h)
                removed.append(service_topic)
            elif(config['service_type'] == 'websocket'):
                handlers_to_remove = []
                for tuble in self.app.handlers:
                    x = tuble[1][0]
                    if(x.handler_class == config['handler']):
                        handlers_to_remove.append(tuble)
                for h in handlers_to_remove:
                    self.app.handlers.remove(h)
                removed.append(service_topic)
        for t in removed:
            self.service_register.remove_service(t)
        
    def add_service(self, config):
        if('host_address' not in config):
            config['host_address'] = self.ip_address
        if('port' not in config):
            config['port'] = self.port
        if(self.service_register.build_topic(config) in self.service_register.services):
            return # skip if exists

        self.service_register.add_service(config)
        
        if('handler' not in config):
            return
        
        path = self.make_path_config(config)
        if(config['service_type'] == 'thread'):
            handler = config["handler"]()
            e = Event()
            t = Thread(target=handler.initialize, args=(self,e))
            t.daemon = True
            self.threads[self.service_register.build_topic(config)] = (t, e)
            t.start()
        elif(config['service_type'] == 'rest'):
            self.app.add_handlers(r'', [path])
        elif(config['service_type'] == 'websocket'):
            self.app.add_handlers(r'', [path])

    def get_services(self, topic):
        return self.service_register.get_services(topic)

    def build_topic(self, config):
        return self.service_register.build_topic(config)

    def __setup_default_settings__(self):
        # add handlers for added services
        if('ui_modules' not in self.settings):
            self.settings["ui_modules"] = {
                "Rest_Service_Module": uim.Rest_Service_Module,
                "Websocket_Service_Module": uim.Websock_Service_Module,
                "Head_Module": uim.Head_Module
                }
        else:
            self.settings["ui_modules"]["Rest_Service_Module"] = uim.Rest_Service_Module
            self.settings["ui_modules"]["Websocket_Service_Module"] = uim.Websock_Service_Module
            self.settings["ui_modules"]["Head_Module"] = uim.Head_Module

    def make_path_config(self, config):
        if "path" in config and "handler_settings" in config:
            # config["handler_settings"]["module"] = self
            return (config["path"],
                    config["handler"],
                    config["handler_settings"])
        elif "path" in config:
            return (config["path"], config["handler"], {"module": self})
        elif "handler_settings" in config:
            #  config["handler_settings"]["module"] = self
            return (self.__make_fall_back_path(config["service_name"]),
                    config["handler"],
                    config["handler_settings"])
        else:
            return (self.__make_fall_back_path(config["service_name"]),
                    config["handler"],
                    {"module": self})

    def __make_fall_back_path(self, service_name):
        return r'\/' + str(service_name) + r"\/|\/" + str(service_name)

    def get_fieldordefault(self, settings, field, default):
        if field in settings:
            return settings[field]
        else:
            return default

    def dispatch_event(self, event_type, event_data):
        event = frameworkEvent(event_type, self.ip_address, event_data)
        self.event_dispatcher.dispatch_event(event)

    def add_event_listener(self, event_type, listener):
        self.event_dispatcher.add_event_listener(event_type, listener)
    # --------------------------------------------------------
    # Exit and termination handlers:
    # --------------------------------------------------------

    def termination_handler(self):
        if(not self.stop_event.is_set()):
            self.dispatch_event('TERMINATING', 'TERMINATING')
            # time.sleep(1)
        # unsubscripe from broker:
        # self.subscribe_to_broker(isSubscribing=False)

        # stop all threads
        self.stop_event.set()
        for key in self.threads:
            t,e = self.threads[key]
            e.set()
        time.sleep(1)
        # stop tornado:
        if(self.is_exiting):
            ioloop.IOLoop.instance().stop()
            self.is_exiting = False

    def exit_handler(self, signal, frame):
        # print("INTERRUPTED! -terminating")
        if(not self.stop_event.is_set()):
            self.dispatch_event('TERMINATING', 'TERMINATING')
            # time.sleep(1)

        # stop all threads
        self.stop_event.set()
        for key in self.threads:
            t,e = self.threads[key]
            e.set()
        time.sleep(1)
        # stop tornado:
        if(self.is_exiting):
            ioloop.IOLoop.instance().stop()
            self.is_exiting = False
        sys.exit(0)
