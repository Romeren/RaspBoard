import atexit  # NOQA
from tornado import web, ioloop  # NOQA
# from service_framework.common import utilities as util
import random as rnd
from service_framework.common import utilities as util
from service_framework.common_modules import ui_modules as uim
from service_framework.events.event_module import Event as frameworkEvent
from service_framework.events.event_module import EventDispatcher as dispatcher
from service_framework.service_container.service_register import service_register
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

    def __init__(self, services, settings={}):
        reload(sys)  
        sys.setdefaultencoding('utf8')
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
        self.configure_module(services)
        # Running Threads:
        self.threads = {}
        self.stop_event = Event()  # Safely stopping services on exits:
        self.is_exiting = True  # Safely stopping services on exits:
        self.start_threads()

        self.__setup_default_settings__()

        self.start_webserver()

    def start_webserver(self):
        # set up tornado frame work:
        self.dispatch_event('LOG', (10, 'Starting webserver...', 'CONTAINER'))
        self.dispatch_event('LOG', (10, 'Webserver listinging on port', self.port))

        paths = []
        self.dispatch_event('LOG', (1, 'Available paths on webserver:'))
        topic = 'rest/.*/.*/' + self.ip_address
        for config in self.get_services(topic):
            path = self.make_path_config(config)
            self.dispatch_event('LOG', (10, path[0]))
            paths.append(path)
        topic = 'websocket/.*/.*/' + self.ip_address
        for config in self.get_services(topic):
            path = self.make_path_config(config)
            self.dispatch_event('LOG', (10, path[0]))
            paths.append(path)

        # add listener to port:
        self.app = web.Application(paths, **self.settings)
        self.app.listen(self.port)
        ioloop.IOLoop.instance().start()

    def start_threads(self):
        self.dispatch_event('LOG', (10, 'Starting threads', 'CONTAINER'))
        topic = 'thread/.*/.*/' + self.ip_address
        for config in self.get_services(topic):
            path = self.make_path_config(config)
            self.dispatch_event('LOG', (10, path[0]))
            module = config["handler"]()
            t = Thread(target=module.initialize, args=(self,
                                                       self.stop_event
                                                       ))
            t.daemon = True
            self.threads[self.service_register.build_topic(config)] = t
            t.start()

    def configure_module(self, services):
        for config in services:
            config['host_address'] = self.ip_address
            config['port'] = self.port
            self.service_register.add_service(config)

    def add_service(self, config):
        self.service_register.add_service(config)

    def get_services(self, topic):
        return self.service_register.get_services(topic)

    def build_topic(self, config):
        return self.service_register.build_topic(config)

    def __setup_default_settings__(self):
        # Add exit handler:
        atexit.register(self.termination_handler)
        signal.signal(signal.SIGINT, self.exit_handler)

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
        time.sleep(1)
        # stop tornado:
        if(self.is_exiting):
            ioloop.IOLoop.instance().stop()
            self.is_exiting = False
        sys.exit(0)
