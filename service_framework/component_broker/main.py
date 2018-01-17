# -*- coding: utf-8 -*-  # NOQA
""" docstring
"""

import json
# from service_framework.events.event_module import Broker_Event
from RaspBoard.service_framework.common import utilities as util
from RaspBoard.service_framework.events.event_module import Service_Changed_Event
import time
import zmq


class PluginClients(object):
    """Wrapper object for holding client information"""
    def __init__(self,
                 service_type,
                 service_name,
                 hostname,
                 port,
                 service_category,
                 time,
                 dependencies=[]):
        self.hostname = hostname
        self.port = port
        self.time = time
        self.service_category = service_category
        self.service_name = service_name
        if service_type not in ["rest", "websocket", 'thread']:
            raise Exception("Not valid service_type")
        self.service_type = service_type
        self.dependencies = dependencies;

    def to_json(self):
        return {"host_address": self.hostname,
                "port": self.port,
                "service_name": self.service_name,
                "service_category": self.service_category,
                "service_type": self.service_type,
                "service_dependencies": self.dependencies}


def handle_get_services(message):
    # gets all the plugins based on provided information:
    # {
    #   get_service_list: {
    #       service_type: <type> ~required
    #       service_category = <category> ~optional
    #       service_name: <name> ~optional
    #       host_address: <address> ~optional
    #   }
    # }
    # or a lookup can be performed by topic:
    # {
    #   get_service_list: {
    #       topic: <path> ~required
    #   }
    # }
    request = message["get_service_list"]
    if("service_type" not in request and "topic" not in request):
        return {"status": 400, "error": "Invalid request!"}

    topic = None
    if "topic" in request:
        topic = request["topic"]
    else:
        topic = util.build_topic_from_request(request)

    clients = util.get_matching(plugins, topic)

    # response:
    reply = {"status": 200, "services": []}
    for service in clients:
        reply["services"].append(plugins[service].to_json())
    return reply


def handle_get_service(message):
    # gets information about a single service!
    # if more than one is found based on supplied information -
    #   the first will be returned!
    # {
    #  get_service : {
    #       service_type : <type>  ~ optional
    #       service_name : <name>  ~ optional
    #       service_category = <category> ~optional
    #       host_address : <address>  ~ optional
    #       ...
    #    }
    # Or a service can be located by topuic:
    #  get_service : {
    #       topic : <topic>  ~ required
    #    }
    # }
    request = message["get_service"]

    topic = None

    if "topic" in request:
        topic = request["topic"]
    else:
        topic = util.build_topic_from_request(request)

    clients = util.get_matching(plugins, topic)

    service = None
    for key in clients:
        service = plugins[key].to_json()
        break

    if service is None:
        return {"status": 400, "error": "No service found!", "topic": topic}

    reply = {"status": 200,
             "message": "Service found",
             "service": service}
    return reply


def handle_plugins_register_unregister(message):
    reply = {"status": 400, "ERROR": "Invalid Message"}
    # print("")
    # print(message)
    subscriping = message["subscribe"]
    port = message["port"]
    topic = util.build_topic_from_request(message)

    if(topic in plugins):
        if subscriping:
            print("Updating time: " + topic)
            plugins[topic].time = time.clock()

            __publish_event(topic, {"event": Service_Changed_Event.UPDATED,
                                    "service": plugins[topic].to_json()})

            reply = {"status": 200,
                     "port": plugins[topic].port,
                     "message": "heartbeat accepted"}
        else:
            print("Removing plugin: ", topic, "port", port)
            removed = plugins.pop(topic, None)

            __publish_event(topic, {"event": Service_Changed_Event.REMOVED,
                                    "service": removed.to_json()})

            reply = {"status": 200, "message": "plugin correctly unsubscriped"}
    elif(subscriping):
        print("Adding plugin: ", topic, "port", port)
        plugin = PluginClients(message["service_type"],
                               message["service_name"],
                               message["host_address"],
                               port,
                               message["service_category"],
                               time.clock(),
                               message["service_dependencies"])

        plugins[topic] = plugin
        __publish_event(topic, {"event": Service_Changed_Event.ADDED, "service": plugin.to_json()})
        reply = {"status": 200,
                 "port": plugins[topic].port,
                 "message": "plugin correctly subscriped"}
    #  Send reply back to client
    return reply


def handle_request_config(message):
    reply = {"status": 400, "ERROR": "Invalid Message"}
    host = message["host"]

    if host is None or host == "":
        return reply

    # Checking if host host multiple plugins:
    candidate = port + 1
    is_requesting_specific_port = False
    if "port" in message:
        is_requesting_specific_port = True
        candidate = message["port"]

    # print("config_in:", message)
    obtained_ports = []
    for plugin in util.get_matching(plugins, "*/*/*/" + host):
        obtained_ports.append(plugins[plugin].port)

    port_taken = True
    while port_taken:
        if is_requesting_specific_port and candidate in obtained_ports:
            reply["message"] = "PORT allready in use!"
            return reply
        elif candidate in obtained_ports:
            candidate += 1
        else:
            port_taken = False

    # TODO(create): randomly gennerated secret:
    application_secret = "__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__"
    # print("assigned port:", candidate)
    reply = {"status": 200,
             "port": candidate,
             "application_secret": application_secret,
             "message": "Port have been assigned"}
    return reply


def __publish_event(topic, message):
    publisher_socket.send_multipart([bytearray(topic, "utf-8"),
                                     bytearray(json.dumps(message), "utf-8")])

plugins = {}  # topic and wrapper class ---
# topic = <service_type>/<service_category>/<service_name/<host_address>
usedports = [5555, 5556]
brokerPort = usedports[0]
publisherPort = usedports[1]
context = zmq.Context()
server_socket = context.socket(zmq.REP)

address = util.get_own_ipaddress()
# address = "192.168.2.30"

server_socket.bind("tcp://" + address + ":" + str(brokerPort))

publisher_socket = context.socket(zmq.PUB)
publisher_socket.bind("tcp://*:%s" % publisherPort)


while True:
    #  Wait for next request from client
    message = server_socket.recv_string()
    port = usedports[len(usedports) - 1]
    message = json.loads(message)
    reply = {"status": 400, "ERROR": "Invalid Message"}

    if("subscribe" in message and
       "host_address" in message and
       "service_name" in message and
       "service_category" in message and
       "service_type" in message and
       "port" in message):
        reply = handle_plugins_register_unregister(message)
    elif("get_service_list" in message):
        reply = handle_get_services(message)
    elif("get_service" in message):
        reply = handle_get_service(message)
    elif("request_config" in message and
         "host" in message):
        reply = handle_request_config(message)

    server_socket.send_string(json.dumps(reply))
