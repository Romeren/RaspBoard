import fnmatch
import re


class service_register(object):
    def __init__(self, module):
        self.remote_services = {}
        self.local_services = {}
        self.module = module

    def get_services(self, topic, allowLocal=True, allowRemote=True):
        # request plugin at broker:
        topic += "/*"
        clients = self.get_matching(self.__get_services(), topic)

        for key in clients:
            yield self.__get_services()[key]

    def get_service(self, topic):
        topic += "/*"
        clients = util.get_matching(self.__get_services(), topic)
        elm = None
        for key in clients:
            elm = self.__get_services()[key]
            break

        return elm

    def add_local_service(self, config):
        config['host_address'] = self.module.ip_address
        config['port'] = self.module.port
        topic = self.build_topic(config)

        self.local_services[topic] = config
        self.module.dispatch_event('SERVICE_ADDED_LOCALLY', (10, topic))

    def remove_service(self, topic):
        self.__get_services().pop(topic, None)

    # --------------------------------------------------------
    # Utiliy functions
    # --------------------------------------------------------
    def __get_services(self, allowLocal=True, allowRemote=True):
        services = {}
        if allowRemote:
            services.update(self.remote_services)
        if allowLocal:
            services.update(self.local_services)
        return services

    def get_matching(self, dictionary, topic):
        # Get matching entries in dictionary, based on topic.
        # use regular expressions
        regex = fnmatch.translate(str(topic))
        reObj = re.compile(regex)
        return (key for key in dictionary if reObj.search(key))

    def build_topic(self, config):
        # takes json:
        # returns topic
        service_type = "*"
        service_category = "*"
        service_name = "*"
        host_address = "*"
        if("service_type" in config):
            service_type = config["service_type"]
        if("service_name" in config):
            service_name = config["service_name"]
        if("host_address" in config):
            host_address = config["host_address"]
        if("service_category" in config):
            service_category = config["service_category"]

        return self.build_topic_from_fields(service_type,
                                            service_category,
                                            service_name,
                                            host_address)

    def build_topic_from_fields(self,
                                service_type,
                                service_category,
                                service_name,
                                host_address):
        topic = service_type + "/" + service_category + "/" + service_name + "/" + host_address  # NOQA
        return topic
