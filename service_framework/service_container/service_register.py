import re


class service_register(object):
    def __init__(self, module):
        self.services = {}
        self.module = module

    def get_services(self, topic):
        # request plugin at broker:
        clients = self.get_matching(self.__get_services(), topic)

        for key in clients:
            yield self.__get_services()[key]

    def get_service(self, topic):
        topic += "/*"
        clients = self.get_matching(self.__get_services(), topic)
        elm = None
        for key in clients:
            elm = self.__get_services()[key]
            break

        return elm

    def add_service(self, config):
        topic = self.build_topic(config)
        self.services[topic] = config
        self.module.dispatch_event('SERVICE_ADDED_LOCALLY', (10, topic))

    def remove_service(self, topic):
        self.__get_services().pop(topic, None)

    # --------------------------------------------------------
    # Utiliy functions
    # --------------------------------------------------------
    def __get_services(self):
        # services = {}
        # if allowRemote:
        #     services.update(self.remote_services)
        # if allowLocal:
        #     services.update(self.local_services)
        return self.services

    def get_matching(self, dictionary, topic):
        # Get matching entries in dictionary, based on topic.
        # use regular expressions
        # regex = fnmatch.translate(str(topic))
        reObj = re.compile(topic)
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
