# -*- coding: utf-8 -*-  # NOQA
from service_framework.plugin_module import Plugin_module as framework  # NOQA

# plugins:
plugins = []

from services.pages.dashboard.restservice import config as dashboard  # NOQA
plugins.append(dashboard)

system_settings = {'port': 8080}
framework(plugins,
          settings=system_settings)
