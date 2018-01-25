# -*- coding: utf-8 -*-  # NOQA
from RaspBoard.service_framework.a_plugin import RestHandler as abstract_plugin  # NOQA


class Service(abstract_plugin):
    def initialize(self, module):
        self.module = module

    def get(self):
        html_path = "html/tile.html"
        context = self.get_basic_context(config)
        self.render_response(html_path, context=context)

config = {"service_name": "slideshow",
          "handler": Service,
          "service_type": "rest",
          "service_category": "tile",
          "dependencies": [
              {'name': 'random_image', 'service': "rest/api/random_image"},
          ]
          }
