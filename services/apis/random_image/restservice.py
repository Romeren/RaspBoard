# -*- coding: utf-8 -*-  # NOQA
import dropbox
import random as rnd
from RaspBoard.service_framework.a_plugin import RestHandler as abstract_plugin  # NOQA


class Service(abstract_plugin):
    def initialize(self, module):
        self.module = module

    def get(self):
        dbx = dropbox.Dropbox('8ojZ64O1QOMAAAAAAAAgtze8RBvwA8iCgBupa5MWwmGblbABMbt7_N0g1qVolt3f')
        files = dbx.files_list_folder('')

        rnd_file = files.entries[rnd.randint(0, len(files.entries))-1]

        link = dbx.files_get_temporary_link(rnd_file.path_lower)

        self.write(link.link.decode('utf-8'))

config = {"service_name": "random_image",
          "handler": Service,
          "service_type": "rest",
          "service_category": "api",
          "dependencies": [
          ]
          }
