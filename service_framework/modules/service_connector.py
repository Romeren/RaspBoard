from service_framework.a_plugin import ThreadHandler as superClass
from service_framework.common.utilities import placeholder as Context
from service_framework.events.event_module import Event as frameworkEvent
from tornado.httpclient import HTTPClient
from tornado.httpclient import HTTPError


class Service(superClass):
    def initialize(self, module, stopevent):
        self.module = module
        self.stopevent = stopevent

        found_event = 'SERVICE_CONTAINER_DISCOVERED'
        self.obtained_event = 'SERVICE_CONTAINER_CONFIGURATION_OPTAINED'
        self.module.add_event_listener(found_event, self.connect)

    def connect(self, event):
        service_addr, broad_cast_port = event.data[0]
        service_port = event.data[1]

        context = Context()
        context = self.set_dependencies(context, config)

        reciever_info = {
            'service_name': context.references.config[0].service_name,
            'host_address': service_addr,
            'port': service_port,
            'service_type': context.references.config[0].service_type
        }

        url = self.get_service_address_from_request(reciever_info)
        url = url + '?authentication=' + self.module.cluster_authentication
        url = url + '&cluster_port=' + str(self.module.cluster_port)

        http_client = HTTPClient()
        try:
            response = http_client.fetch(url)
            if(response.body != None):
                response = self.load_message(response.body)
                self.module.dispatch_event(self.obtained_event, response)
        except HTTPError as e:
            self.module.dispatch_event('LOG', (1, e, config['service_name']))
        except Exception as e:
            self.module.dispatch_event('LOG', (1, e, config['service_name']))
        http_client.close()


config = {
    "service_name": "builtin/service_connector",
    "handler": Service,
    "service_type": "thread",
    "service_category": "system",
    "dependencies": [
        {'name': 'config',
         'service':  'rest/system/builtin/service_configurator'}
    ]
}
