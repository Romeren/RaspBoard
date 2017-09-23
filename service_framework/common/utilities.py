# -*- coding: utf-8 -*-  # NOQA
# --------------------------------------------------------
# Utilities
# --------------------------------------------------------

import fcntl
import fnmatch
import re
import socket
import struct


def get_own_ipaddress():
    # TODO(): GENERALIZE SOLUTION:
    iface = 'eth0'
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', iface[:15])
    )[20:24])


def get_matching(dictionary, topic):
    # Get matching entries in dictionary, based on topic.
    # use regular expressions
    regex = fnmatch.translate(str(topic))
    reObj = re.compile(regex)
    return (key for key in dictionary if reObj.search(key))


def build_topic_from_request(request):
    # takes json:
    # returns topic
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

    return build_topic(service_type,
                       service_category,
                       service_name,
                       host_address)


def build_topic(service_type, service_category, service_name, host_address):
    topic = service_type + "/" + service_category + "/" + service_name + "/" + host_address  # NOQA
    return topic
