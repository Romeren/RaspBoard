# -*- coding: utf-8 -*-  # NOQA
from container import Container

services = []

from system_services.service_starter import config as starter
from system_services.service_stopper import config as stopper

# from system_services.cluster_publisher import config as pub
# from system_services.cluster_subscriber import config as sub
# from system_services.service_registry_share import config as share
from system_services.service_terminal_log import config as log
# from system_services.service_configurator import config as config
# from system_services.service_discovery import config as discovery
# from system_services.service_connector import config as connector

services.append(log)
services.append(starter)
services.append(stopper)
# services.append(pub)
# services.append(sub)
# services.append(share)
# services.append(config)
# services.append(discovery)
# services.append(connector)

from common.read_file import get_key_content, get_id

raspboard_id = get_id('raspboard.id')
cluster_authentication = get_key_content('cluster_key.key')
system_settings = {
                   'raspboard_id': raspboard_id,
                   'port': 8080,
                   'discovery_port': 9999,
                   'cluster_port': 9998,
                   'cluster_authentication': cluster_authentication,
                   'LOG_LEVEL': '0'
                   }
container = Container(settings=system_settings)

for s in services:
    container.add_service(s)


# import requests
# import json
# import cPickle as pickle

# handler = log['handler']
# log['handler'] = pickle.dumps(handler)
# msg = json.dumps(log)
# r = requests.post("http://192.168.2.15:8080/builtin/service_starter", data={'config': msg})
# print(r.status_code, r.reason)

# handler = config['handler']
# config['handler'] = pickle.dumps(handler)
# msg = json.dumps(config)
# r = requests.post("http://192.168.2.15:8080/builtin/service_starter", data={'config': msg})
# print(r.status_code, r.reason)



# msg = container.service_register.build_topic(config)
# r = requests.post("http://192.168.2.15:8080/builtin/service_stopper", data={'topic': msg})
# print(r.status_code, r.reason)



raw_input('-------HIT-ENTER-TO-QUIT--------')


# from plugin_module import Plugin_module as framework  # NOQA
#
# from services.misc.restserver import config as java  # NOQA
# plugins.append(java)
#
# # tiles
# from services.tiles.clock.restservice import config as clock  # NOQA
# plugins.append(clock)
#
#
# # page
# from services.pages.dashboard.restservice import config as dashboard  # NOQA
# plugins.append(dashboard)
#
# # chrome cast hook
# from services.pages.casthook.restservice import config as cast  # NOQA
# plugins.append(cast)
#
#
# system_settings = {'port': 8080}
# framework(plugins,
#           settings=system_settings)
