# -*- coding: utf-8 -*-  # NOQA
from service_framework.plugin_module import Plugin_module as framework  # NOQA

# plugins:
plugins = []

from  core.logging.socketservice import config as log
plugins.append(log)

framework(plugins)


