# -*- coding: utf-8 -*-  # NOQA
import dropbox
import random as rnd
import time
from RaspBoard.service_framework.a_plugin import RestHandler as abstract_plugin  # NOQA


url_cache = []
last_renewed_cach_at = 0


class Service(abstract_plugin):
    def initialize(self, module):
        self.module = module

    def get(self):
        global url_cache
        global last_renewed_cach_at

        image_id = self.get_argument('image_id', None)
        if(image_id is not None):
            try:
                image_id = int(image_id)
            except Exception as e:
                print(e)
                image_id = None

        current_time = time.time()
        if current_time - last_renewed_cach_at > (60 * 60 * 3):
            last_renewed_cach_at = current_time
            url_cache = []
            print('RENEWING CACHE..!')
            dbx = dropbox.Dropbox('8ojZ64O1QOMAAAAAAAAgtze8RBvwA8iCgBupa5MWwmGblbABMbt7_N0g1qVolt3f')
            files = dbx.files_list_folder('')
            no_of_files = len(files.entries)
            for i in range(0, no_of_files):
                path = files.entries[i].path_lower
                print(path)
                link = dbx.files_get_temporary_link(path).link.decode('utf-8')
                print(link)
                url_cache.append(link)

            # url_cache = [dbx.files_get_temporary_link(f.path.lower).link.decode('utf-8') for f in files.entries]

        file_url = None
        if(image_id is not None):
            index = image_id % len(url_cache)
            file_url = url_cache[index]
        else:
            file_url = url_cache[rnd.randint(0, len(url_cache)-1)]
        print('CAHCE_LEN', str(len(url_cache)))
        print('URL', file_url)
        self.write(file_url)

config = {"service_name": "random_image",
          "handler": Service,
          "service_type": "rest",
          "service_category": "api",
          "dependencies": [
          ]
          }
