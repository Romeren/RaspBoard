# -*- coding: utf-8 -*-  # NOQA
from service_framework.plugin_module import Plugin_module as framework  # NOQA

# plugins:
plugins = []

from services.misc.restserver import config as java  # NOQA
plugins.append(java)

# tiles
from services.tiles.clock.restservice import config as clock  # NOQA
plugins.append(clock)


# page
from services.pages.dashboard.restservice import config as dashboard  # NOQA
plugins.append(dashboard)


system_settings = {'port': 8080}
framework(plugins,
          settings=system_settings)
