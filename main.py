# -*- coding: utf-8 -*-  # NOQA
from RaspBoard.container import Container


from RaspBoard.system_services.service_starter import config as starter
from RaspBoard.system_services.service_loader import config as loader
from RaspBoard.system_services.service_stopper import config as stopper
from RaspBoard.system_services.service_terminal_log import config as log


services = []
services.append(log)
services.append(starter)
services.append(stopper)
services.append(loader)

from common.read_file import get_key_content, get_id

raspboard_id = get_id('raspboard.id')
cluster_authentication = get_key_content('RaspBoard/cluster_key.key')
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


raw_input('-------HIT-ENTER-TO-QUIT--------')

