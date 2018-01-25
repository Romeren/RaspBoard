# -*- coding: utf-8 -*-  # NOQA

from service_framework.service_container.container import Container as framework
# plugins:
plugins = []

from service_framework.modules.service_terminal_log import config as log
plugins.append(log)

from service_framework.modules.service_configurator import config as config
plugins.append(config)

from service_framework.modules.service_discovery import config as discovery
plugins.append(discovery)

from service_framework.modules.service_connector import config as connector
plugins.append(connector)


system_settings = {'port': 8080,
                   'discovery_port': 9999,
                   'LOG_LEVEL': 'ALL'
                   }
framework(plugins,
          settings=system_settings)

raw_input('PRESS')
# from service_framework.plugin_module import Plugin_module as framework  # NOQA
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
