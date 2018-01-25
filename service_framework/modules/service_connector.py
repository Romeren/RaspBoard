from service_framework.a_plugin import ThreadHandler as superClass
from service_framework.events.event_module import Event as frameworkEvent
from tornado.httpclient import HTTPClient
from tornado.httpclient import HTTPError


class Service(superClass):
    def initialize(self, module, stopevent):
        self.module = module
        self.stopevent = stopevent

        found_event = 'SERVICE_CONTAINER_DISCOVERED'
        self.module.event_dispatcher.add_event_listener(found_event,
                                                        self.connect)

    def connect(self, event):
        service_addr, broad_cast_port = event.data[0]
        service_port = event.data[1]
        # TODO(): service_name is hardcoded and must be changed:
        service_name = "builtin/service_configurator"
        context = {}
        context = self.set_dependencies(context, config)
        for x in context.config:
            print(x)
        # print(service_addr, service_port)

        http_client = HTTPClient()
        try:
            response = http_client.fetch("http://%s:%s/%s" % (service_addr,
                                                              service_port,
                                                              service_name
                                                              ))
            print(response.body)
        except HTTPError as e:
            event = frameworkEvent('LOG',
                                   data=(1,
                                         e,
                                         config['service_name']
                                         ))

            self.module.event_dispatcher.dispatch_event(event)
        except Exception as e:
            event = frameworkEvent('LOG',
                                   data=(1,
                                         e,
                                         config['service_name']
                                         ))

            self.module.event_dispatcher.dispatch_event(event)
        http_client.close()


config = {
    "service_name": "builtin/service_connector",
    "handler": Service,
    "service_type": "thread",
    "service_category": "system",
    "dependencies": [
        {'name': 'config', 'service':  'rest/system/builtin/service_configurator'}
    ]
}
