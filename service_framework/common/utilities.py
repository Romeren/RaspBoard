# -*- coding: utf-8 -*-  # NOQA
# --------------------------------------------------------
# Utilities
# --------------------------------------------------------

import fnmatch
import re
import socket


def get_own_ipaddress():
    # TODO(): GENERALIZE SOLUTION:

    ips = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]
    return ips


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
