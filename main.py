# -*- coding: utf-8 -*-  # NOQA
from container import Container as framework
# plugins:
plugins = []

from system_services.cluster_publisher import config as pub
from system_services.cluster_subscriber import config as sub

plugins.append(pub)
plugins.append(sub)

from system_services.service_registry_share import config as share
plugins.append(share)

from system_services.service_terminal_log import config as log
plugins.append(log)

from system_services.service_configurator import config as config
plugins.append(config)

from system_services.service_discovery import config as discovery
plugins.append(discovery)

from system_services.service_connector import config as connector
plugins.append(connector)

from system_services.Killer import config as kill
plugins.append(kill)

from common.read_file import get_content, get_id

raspboard_id = get_id('raspboard.id')
cluster_authentication = get_content('cluster_key.key')
system_settings = {
                   'raspboard_id': raspboard_id,
                   'port': 8080,
                   'discovery_port': 9999,
                   'cluster_port': 9998,
                   'cluster_authentication': cluster_authentication,
                   'LOG_LEVEL': '0'
                   }
framework(plugins,
          settings=system_settings)





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
