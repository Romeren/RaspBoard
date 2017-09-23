# -*- coding: utf-8 -*-  # NOQA
""" Wrapper for implementations of plugins!
handles subscriping to server and sending heartbeats.
"""

import atexit
import fcntl
import fnmatch
import json
import re
from service_framework.common_modules import ui_modules as uim
from service_framework.events.event_module import Event as frameworkEvent
from service_framework.events.event_module import EventDispatcher as dispatcher
from service_framework.events.event_module import Service_Changed_Event as service_changed  # NOQA
import signal
import socket
import struct
import time
from tornado import web, ioloop  # NOQA
from threading import Event
from threading import Thread
import zmq


class Plugin_module(object):

    def __init__(self, service_configurations, settings={}):
        self.is_active = True
        self.is_exiting = False
        # self.heartbeat_interval = 120.0
        self.address = self.get_own_ipaddress()
        self.port = 5555
        self.pluginPort = None
        self.threads = []
        self.service_configurations = service_configurations
        self.settings = settings
        self.stop_event = Event()
        self.event_dispatcher = dispatcher()
        self.plugins = None

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


        #  Add exit handler:
        atexit.register(self.termination_handler)
        #  add interrupt handler
        #  signal.signal(signal.SIGBREAK, self.exit_handler)
        #  signal.signal(signal.SIGABRT, self.exit_handler)
        #  signal.signal(signal.SIGILL, self.exit_handler)
        signal.signal(signal.SIGINT, self.exit_handler)
        #  signal.signal(signal.SIGSEGV, self.exit_handler)
        #  signal.signal(signal.SIGTERM, self.exit_handler)

        app = self.configure_module()

        subscriber = Thread(target=self.broker_event_subscriber,
                            args=(self.address, self.port+1, self.stop_event))
        subscriber.start()
        # TEST:
        # self.broker_event_subscriber(self.address,
        #                              self.port +1,
        #                              self.stop_event)

        # start all threads:
        for t in self.threads:
            t.start()
        self.start_webserver(app)

# --------------------------------------------------------
# Utilities
# --------------------------------------------------------
    def get_own_ipaddress(slef):
        # TODO(): GENERALIZE SOLUTION:
        iface = 'eth0'
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', iface[:15])
        )[20:24])

# --------------------------------------------------------
# Broker request functions
# --------------------------------------------------------
    def start_webserver(self, app):
        # add listener to port:
        app.listen(self.pluginPort)
        print("Module started!")
        ioloop.IOLoop.instance().start()

    def configure_module(self):
        # Connect to plugin broker:
        self.__connect_to_broker()

        # Request configuration:
        #   - Request available port
        self.request_config()

        # Subscribe module to plugin broker:
        self.subscribe_to_broker(isSubscribing=True)

        # configure tornado server for handling websockets:
        if(self.pluginPort is None):
            print("plugin port not configured!")
            exit()

        # build paths:
        paths = []
        threads = []
        for config in self.service_configurations:
            if config['service_type'] == "thread":
                threads.append(config)
                continue
            paths.append(self.__make_path_config(config))

        # set cookie secret:
        self.settings["cookie_secret"] = self.application_secret

        # start thread modules:
        for t in threads:
            module = t['handler']()
            thread = Thread(target=module.initialize, args=(self, self.stop_event))
            self.threads.append(thread)

        # set up tornado frame work:
        return web.Application(paths, **self.settings)

    def __connect_to_broker(self):
        context = zmq.Context()
        # Connect to plugin broker:
        print("Connecting to server...")
        self.socket = context.socket(zmq.REQ)
        self.socket.connect("tcp://" + self.address + ":" + str(self.port))

    def get_plugins_from_broker(self,
                                service_type="*",
                                service_category="*",
                                service_name="*",
                                host_address="*",
                                topic=None):
        if topic is None:
            request = {"get_service_list":
                       {
                           "service_type": service_type,
                           "service_category": service_category,
                           "service_name": service_name,
                           "host_address": host_address
                           }
                       }
        else:
            request = {"get_service_list":
                       {
                           "topic": topic
                           }
                       }
        # print("get_plugin", request)

        self.socket.send_string(json.dumps(request))

        message = self.socket.recv_string()
        message = json.loads(message)
        if(message["status"] == 200):
            # print("broker_answer", message)
            return message["services"]
        else:
            print(message)
            self.is_active = False
            exit()

    def request_config(self):
        request = {
            "request_config": True,
            "host": self.address
            }
        if "port" in self.settings:
            request["port"] = self.settings["port"]
            del self.settings["port"]

        self.socket.send_string(json.dumps(request))

        #  Get the reply.
        message = self.socket.recv_string()
        message = json.loads(message)
        if(message["status"] == 200):
            # print("Received reply ", message)
            self.pluginPort = message["port"]
            self.application_secret = message["application_secret"]
        else:
            print(message)
            self.is_active = False
            exit()

    def subscribe_to_broker(self, isSubscribing):
        for config in self.service_configurations:
            dependencies = []

            if("dependencies" not in config):
                config["dependencies"] = []

            for dep in config["dependencies"]:
                dependencies.append(dep["service"])
            request = {
                "service_name": config["service_name"],
                "host_address": self.address,
                "subscribe": isSubscribing,
                "service_type": config["service_type"],
                "service_category": config["service_category"],
                "port": self.pluginPort,
                "service_dependencies": dependencies}
            self.socket.send_string(json.dumps(request))
            #  Get the reply.
            message = self.socket.recv_string()
            message = json.loads(message)
            if(message["status"] == 200):
                print("Received reply ", message)
                if "port" in message:
                    self.pluginPort = message["port"]
            else:
                print(message)
                self.is_active = False
                exit()

# --------------------------------------------------------
# Publish subscripe functions
# --------------------------------------------------------
    def get_services(self, topic):
        # request plugin at broker:
        topic += "/*"
        clients = self.__get_matching(self.__get_services(), topic)

        elm = []
        for key in clients:
            yield self.__get_services()[key]
            #elm.append(self.__get_services()[key])

        #return elm

    def get_service(self, topic):
        topic += "/*"
        clients = self.__get_matching(self.__get_services(), topic)
        elm = None
        for key in clients:
            elm = self.__get_services()[key]
            break

        return elm

    def build_topics_for_subscribtion(self):
        fields = ["service_type",
                  "service_category",
                  "service_name"]
        topics = []

        # add a default dependency for javascript libs:
        javascrTopic = "rest/miscellanceous/javascripts"
        topics.append(javascrTopic)
        plugins = self.get_plugins_from_broker(topic=(javascrTopic + "/*"))
        for service in plugins:
                        topic = self.__build_topic_from_request(service)
                        topics.append(topic)
                        self.__get_services()[topic] = service

        # add all dependencies for the configurations:
        for config in self.service_configurations:
            topic = self.__build_topic(config[fields[0]],
                                       config[fields[1]],
                                       config[fields[2]],
                                       self.address)
            topics.append(topic)

            plugin = self.get_plugins_from_broker(config[fields[0]],
                                                  config[fields[1]],
                                                  config[fields[2]],
                                                  self.address)[0]
            self.__get_services()[topic] = plugin

            if "dependencies" in config:
                for dep in config["dependencies"]:
                    topics.append(dep["service"])
                    plugins = self.get_plugins_from_broker(topic=(dep["service"] + "/*"))
                    for service in plugins:
                        topic = self.__build_topic_from_request(service)
                        topics.append(topic)
                        self.__get_services()[topic] = service
        # print("topics for plugin", topics)
        # print("plugins_found ", self.__get_services())
        return topics

    def broker_event_subscriber(self, broker_address, broker_port, stop_event):
        print("SUBSCRIBER HAVE BEEN STARTED!")

        context = zmq.Context()
        socket = context.socket(zmq.SUB)
        bk_url = "tcp://" + broker_address + ":" + str(broker_port)
        socket.connect(bk_url)

        topics = self.build_topics_for_subscribtion()

        topics = list(set(topics))  # make sure all are unique!

        # SUBSCRIBE for topics:
        for topic in topics:
            # print('TOPIC', topic)
            socket.setsockopt_string(zmq.SUBSCRIBE, unicode(topic))

        # initiate listener:
        poller = zmq.Poller()
        poller.register(socket, zmq.POLLIN)
        while (not stop_event.is_set()):
            socks = dict(poller.poll(1000))
            if socket in socks and socks[socket] == zmq.POLLIN:
                [topic, content] = socket.recv_multipart()
                info = json.loads(content.decode("utf-8"))

                print(info["event"], topic)

                event = None
                if info["event"] == service_changed.REMOVED:
                    self.__get_services().pop(topic, None)
                    event = frameworkEvent(service_changed.REMOVED, data=(topic, info["service"]))

                elif info['event'] == service_changed.UPDATED:
                    self.__get_services()[topic] = info["service"]
                    event = frameworkEvent(service_changed.UPDATED, data=(topic, info["service"]))
                elif info['event'] == service_changed.ADDED:
                    self.__get_services()[topic] = info["service"]
                    event = frameworkEvent(service_changed.ADDED, data=(topic, info["service"]))

                self.event_dispatcher.dispatch_event(event)
        print("SUBSCRIBER HAVE BEEN TERMINATED!")

# --------------------------------------------------------
# Utiliy functions
# --------------------------------------------------------
    def __get_services(self):
        if self.plugins is None:
            self.plugins = {}
        return self.plugins

    def __make_path_config(self, config):
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

    def __build_topic_from_request(self, request):
        service_type = "*"
        service_category = "*"
        service_name = "*"
        host_address = "*"
        if("service_type" in request):
            service_type = request["service_type"]
        if("service_name" in request):
            service_name = request["service_name"]
        if("host_address" in request):
            host_address = request["host_address"]
        if("service_category" in request):
            service_category = request["service_category"]

        return self.__build_topic(service_type,
                                  service_category,
                                  service_name,
                                  host_address)

    def __build_topic(self,
                      service_type,
                      service_category,
                      service_name,
                      host_address):
        topic = service_type + "/" + service_category + "/" + service_name + "/" + host_address  # NOQA
        return topic

    def __get_matching(self, dictionary, topic):
        regex = fnmatch.translate(str(topic))
        reObj = re.compile(regex)
        return (key for key in dictionary if reObj.search(str(key)))

# --------------------------------------------------------
# Exit and termination handlers:
# --------------------------------------------------------
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
