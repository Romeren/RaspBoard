
class service_register(object):
    """docstring for service_register"""
    def __init__(self, arg):
        super(service_register, self).__init__()
        self.plugins = None
    

    def get_services(self, topic):
        # request plugin at broker:
        topic += "/*"
        clients = util.get_matching(self.__get_services(), topic)

        elm = []
        for key in clients:
            yield self.__get_services()[key]
            #elm.append(self.__get_services()[key])

        #return elm

    def get_service(self, topic):
        topic += "/*"
        clients = util.get_matching(self.__get_services(), topic)
        elm = None
        for key in clients:
            elm = self.__get_services()[key]
            break

        return elm

    def add_service(self, topic, service):
        self.__get_services()[topic] = service

    def remove_service(self, topic):
        self.__get_services().pop(topic, None)

    # --------------------------------------------------------
    # Utiliy functions
    # --------------------------------------------------------
    def __get_services(self):
        if self.plugins is None:
            self.plugins = {}
        return self.plugins

    def __make_path_config(self, config):
        if "path" in config and "handler_settings" in config:
            # config["handler_settings"]["module"] = self
            return (config["path"],
                    config["handler"],
                    config["handler_settings"])
        elif "path" in config:
            return (config["path"], config["handler"], {"module": self})
        elif "handler_settings" in config:
            #  config["handler_settings"]["module"] = self
            return (self.__make_fall_back_path(config["service_name"]),
                    config["handler"],
                    config["handler_settings"])
        else:
            return (self.__make_fall_back_path(config["service_name"]),
                    config["handler"],
                    {"module": self})

    def __make_fall_back_path(self, service_name):
        return r'\/' + str(service_name) + r"\/|\/" + str(service_name)
