# -*- coding: utf-8 -*-  # NOQA
import random as rnd
from RaspBoard.service_framework.a_plugin import RestHandler as abstract_plugin  # NOQA


class Service(abstract_plugin):
    def initialize(self, module):
        self.module = module

    def get(self):
        url = 'https://picsum.photos/200/300/?image=' + str(rnd.randint(1, 400))
        self.write(url)

config = {"service_name": "random_image",
          "handler": Service,
          "service_type": "rest",
          "service_category": "api",
          "dependencies": [
          ]
          }
