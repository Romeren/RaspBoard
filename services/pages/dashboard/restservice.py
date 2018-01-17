# -*- coding: utf-8 -*-  # NOQA
from RaspBoard.service_framework.a_plugin import RestHandler as abstract_plugin  # NOQA


class Service(abstract_plugin):
    def initialize(self, module):
        self.module = module

    def get(self):
        html_path = "html/home.html"
        context = self.get_basic_context(config)
        self.render_response(html_path, context=context)

config = {"service_name": "home",
          "handler": Service,
          "service_type": "rest",
          "service_category": "page",
          "dependencies": [
              {'name': 'tiles', 'service': "rest/tile/*"},
          ]
          }
