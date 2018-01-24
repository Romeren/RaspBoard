# -*- coding: utf-8 -*-  # NOQA
from RaspBoard.service_framework.plugin_module import Plugin_module as framework  # NOQA

# plugins:
plugins = []

from RaspBoard.services.misc.restserver import config as java  # NOQA
plugins.append(java)

# tiles
from RaspBoard.services.tiles.clock.restservice import config as clock  # NOQA
plugins.append(clock)
from RaspBoard.services.tiles.slideshow.restservice import config as slide  # NOQA
plugins.append(slide)

# pages
from RaspBoard.services.pages.dashboard.restservice import config as dashboard  # NOQA
plugins.append(dashboard)

# chrome cast hook
from RaspBoard.services.pages.casthook.restservice import config as cast  # NOQA
plugins.append(cast)

# API's
from RaspBoard.services.apis.random_image.restservice import config as rnd
plugins.append(rnd)

system_settings = {'port': 8080}
framework(plugins,
          settings=system_settings)
